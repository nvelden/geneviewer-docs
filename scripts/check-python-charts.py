"""Check the Python shown with the charts of the guide and the examples: it makes the chart's spec.

Usage, with geneviewer-py installed:

    python scripts/check-python-charts.py

The Python of a chart is python/charts/<id>.py. The files of the guide run in
its order, after python/charts/_setup.py and in one namespace, as a reader
would run them: a snippet can use a table an earlier one made. The files of
the examples page each run on their own: they import and load what they use. The chart a
file ends with must give the spec in site/public/charts/<id>.json, which was
recorded from R, under the rules geneviewer-py's own tests compare specs
with R by:

- an array of one element equals the element (R writes a vector of one as a
  scalar), except under "clusters" and "selection";
- numbers are equal within 1e-9 relative difference;
- a missing key equals null, and [] equals {}; key order does not matter.

One chart draws numbers at random (RANDOM below); there random.randint()
gives the numbers R drew.

Fails when a chart that shows code has no Python, when a file
is no longer used, or when a spec differs.
"""

import ast
import json
import re
import sys
import warnings
from pathlib import Path

from spec_differences import differences

root = Path(__file__).resolve().parents[1]
charts = root / "site" / "public" / "charts"
code = root / "python" / "charts"

# Charts whose data R drew at random, and the column: random.randint() gives
# R's numbers while the chart's file runs, so the charts after it get R's data
RANDOM = {"guide-links-3": "identity"}


class RecordedRandom:
    """Stands in for the random module: randint() gives the recorded numbers."""

    def __init__(self, values):
        self.values = iter([1 if v is None else v for v in values])

    def randint(self, low, high):
        return next(self.values)


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
examples = [chart for section in json.loads((root / "site" / ".vitepress" / "examples.json").read_text(encoding="utf-8"))
            for chart in section["charts"]]
# The chart of "What is geneviewer?", on its own as the examples
examples.append("interactive")
files = {p.stem for p in code.glob("*.py") if not p.stem.startswith("_")}
problems = [f"{i}: no python/charts/{i}.py" for i in [*ids, *examples] if i not in files]
problems += [f"python/charts/{i}.py: not a chart of the guide or the examples"
             for i in sorted(files - set(ids) - set(examples))]

scope = {}
exec((code / "_setup.py").read_text(encoding="utf-8"), scope)
checked = 0
for chart_id in [*ids, *examples]:
    if chart_id not in files:
        continue
    if chart_id in examples:
        scope = {}
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
    # The site's charts are as wide as the page: the export keeps a chart's
    # width beside its spec (scripts/write-chart.R)
    if "width" not in expected:
        actual.pop("width", None)
    found = differences(expected, actual)
    checked += 1
    problems += [f"{chart_id}: {where}: R {json.dumps(e)[:90]}, Python {json.dumps(a)[:90]}"
                 for where, e, a in found[:6]]

if problems:
    sys.exit("\n".join(problems))
print(f"python charts: the Python of {checked} charts gives the chart's spec")
