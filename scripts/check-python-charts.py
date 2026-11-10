"""Check the Python shown with the guide's charts: it makes the chart's spec.

Usage, with geneviewer-py installed:

    python scripts/check-python-charts.py

The Python of a chart is python/charts/<id>.py. The files run in the order of
the guide, after python/charts/_setup.py and in one namespace, as a reader
would run them: a snippet can use a table an earlier one made. The chart a
file ends with must give the spec in site/public/charts/<id>.json, which was
recorded from R, under the rules geneviewer-py's own tests compare specs
with R by:

- an array of one element equals the element (R writes a vector of one as a
  scalar), except under "clusters" and "selection";
- numbers are equal within 1e-9 relative difference;
- a missing key equals null, and [] equals {}; key order does not matter.

One chart draws numbers at random (RANDOM below); there random.randint()
gives the numbers R drew.

Fails when a chart of the guide that shows code has no Python, when a file
is no longer used, or when a spec differs.
"""

import ast
import json
import re
import sys
import warnings
from pathlib import Path

root = Path(__file__).resolve().parents[1]
charts = root / "site" / "public" / "charts"
code = root / "python" / "charts"

ALWAYS_ARRAYS = ("clusters", "selection")
# Charts whose data R drew at random, and the column: random.randint() gives
# R's numbers while the chart's file runs, so the charts after it get R's data
RANDOM = {"guide-links-3": "identity"}


class RecordedRandom:
    """Stands in for the random module: randint() gives the recorded numbers."""

    def __init__(self, values):
        self.values = iter([1 if v is None else v for v in values])

    def randint(self, low, high):
        return next(self.values)


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def differences(expected, actual, path=(), out=None):
    out = [] if out is None else out
    if (path[-1] if path else None) not in ALWAYS_ARRAYS:
        if isinstance(expected, list) and len(expected) == 1:
            expected = expected[0]
        if isinstance(actual, list) and len(actual) == 1:
            actual = actual[0]
    empty = lambda x: isinstance(x, (list, dict)) and not x  # noqa: E731
    if (expected is None and actual is None) or (empty(expected) and empty(actual)):
        return out
    where = ".".join(str(p) for p in path)
    if is_number(expected) and is_number(actual):
        scale = max(abs(expected), abs(actual))
        if expected != actual and abs(expected - actual) > 1e-9 * max(scale, 1e-3):
            out.append((where, expected, actual))
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            out.append((where, expected, actual))
        else:
            for i, (e, a) in enumerate(zip(expected, actual)):
                if (e is None) != (a is None):
                    out.append((f"{where}.{i}", e, a))
                else:
                    differences(e, a, (*path, i), out)
    elif isinstance(expected, dict) and isinstance(actual, dict):
        for name in dict.fromkeys([*expected, *actual]):
            differences(expected.get(name), actual.get(name), (*path, name), out)
    elif type(expected) is not type(actual) or expected != actual:
        out.append((where, expected, actual))
    return out


def run(source, scope):
    """Run a snippet; gives the value of the expression it ends with."""
    tree = ast.parse(source)
    last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    exec(compile(tree, "<chart>", "exec"), scope)
    if last is None:
        return None
    return eval(compile(ast.Expression(last.value), "<chart>", "eval"), scope)


guide = (root / "site" / "getting-started.md").read_text(encoding="utf-8")
ids = [m[1] for m in re.finditer(r"^@chart ([\w-]+)((?: \w+)*)$", guide, re.M)
       if "nocode" not in m[2].split()]
files = {p.stem for p in code.glob("*.py") if not p.stem.startswith("_")}
problems = [f"{i}: no python/charts/{i}.py" for i in ids if i not in files]
problems += [f"python/charts/{i}.py: not a chart of the guide" for i in sorted(files - set(ids))]

scope = {}
exec((code / "_setup.py").read_text(encoding="utf-8"), scope)
checked = 0
for chart_id in ids:
    if chart_id not in files:
        continue
    expected = json.loads((charts / f"{chart_id}.json").read_text(encoding="utf-8"))["spec"]
    if chart_id in RANDOM:
        sys.modules["random"] = RecordedRandom(expected["data"][RANDOM[chart_id]])
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            chart = run((code / f"{chart_id}.py").read_text(encoding="utf-8"), scope)
            actual = chart.to_spec()
    except Exception as error:  # noqa: BLE001
        problems.append(f"{chart_id}: {type(error).__name__}: {error}")
        continue
    finally:
        if chart_id in RANDOM:
            del sys.modules["random"]
    found = differences(expected, actual)
    checked += 1
    problems += [f"{chart_id}: {where}: R {json.dumps(e)[:90]}, Python {json.dumps(a)[:90]}"
                 for where, e, a in found[:6]]

if problems:
    sys.exit("\n".join(problems))
print(f"python charts: the Python of {checked} charts gives the chart's spec")
