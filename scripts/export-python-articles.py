"""Make the Python articles: runs articles/python/<name>.md and writes the page
site/python/articles/<name>.md and its charts. The code on a page is the code
that ran. Any error stops the export.

Needs geneviewer-py installed (with the align extra), GENEVIEWER_TUTORIALS_DIR
(a checkout of nvelden/geneviewer-tutorials, for the data) and, for the MUMmer
article, MUMmer. Run from the repo root:

    python scripts/export-python-articles.py            # all
    python scripts/export-python-articles.py gff fasta  # some

A source is Markdown that starts with its title (# ...). Its Python blocks run
in order, in one namespace:

    ```python          shown and run
    ```python hide     run, not shown: for the paths of the data
    ```python norun    shown, not run: for the paths a reader would use

A block that ends with a chart puts the chart below it; one that ends with
table(data) puts the first rows of the table there (table(data, rows=6)).
TUTORIALS is the folder of the data.

The articles are the R articles in Python, and most charts are the same. A
chart whose spec equals the R article's chart of the same number is shown
from that file (site/public/charts/article-<name>-<n>.json); otherwise it
gets its own, python-article-<name>-<n>.json. The export says which.
"""

import ast
import importlib.util
import json
import os
import re
import sys
import warnings
from pathlib import Path

import pandas as pd

from geneviewer import GC

root = Path(__file__).resolve().parents[1]
sources = root / "articles" / "python"
pages = root / "site" / "python" / "articles"
charts = root / "site" / "public" / "charts"
tutorials = Path(os.environ.get("GENEVIEWER_TUTORIALS_DIR", ""))
if not os.environ.get("GENEVIEWER_TUTORIALS_DIR") or not tutorials.is_dir():
    sys.exit("Set GENEVIEWER_TUTORIALS_DIR.")

# The rules a Python spec is compared with R's by
spec_check = importlib.util.spec_from_file_location("check", root / "scripts" / "spec_differences.py")
check = importlib.util.module_from_spec(spec_check)
spec_check.loader.exec_module(check)


class Table:
    def __init__(self, data, rows):
        self.data, self.rows = data, rows


def table(data, rows=6):
    """The first rows of a table, shown below the block."""
    return Table(data, rows)


def cell(value):
    if value is None or value is pd.NA or (isinstance(value, float) and value != value):
        return "NA"
    text = str(int(value)) if isinstance(value, float) and value.is_integer() else str(value)
    return text.replace("|", "\\|").replace("<", "&lt;").replace("{{", "&#123;&#123;").replace("\n", " ")


def table_markdown(shown):
    data = shown.data.head(shown.rows)
    lines = ["| " + " | ".join(map(str, data.columns)) + " |", "|" + " --- |" * len(data.columns)]
    lines += ["| " + " | ".join(cell(v) for v in row) + " |" for row in data.itertuples(index=False)]
    return "\n".join(lines)


def run(source, scope):
    tree = ast.parse(source)
    last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    exec(compile(tree, "<article>", "exec"), scope)
    return None if last is None else eval(compile(ast.Expression(last.value), "<article>", "eval"), scope)


def export(name):
    text = (sources / f"{name}.md").read_text(encoding="utf-8")
    for old in charts.glob(f"python-article-{name}-*.json"):
        old.unlink()
    scope = {"table": table, "TUTORIALS": tutorials}
    page = [f"<!-- Made by scripts/export-python-articles.py from articles/python/{name}.md. Edit that. -->\n\n"]
    count = same = 0
    parts = re.split(r"^```python([^\n]*)\n(.*?)^```[ \t]*$", text, flags=re.M | re.S)
    for i in range(0, len(parts), 3):
        page.append(parts[i])
        if i + 2 >= len(parts):
            break
        option, code = parts[i + 1].strip(), parts[i + 2].rstrip("\n")
        if option not in ("", "hide", "norun"):
            sys.exit(f"{name}: unknown block option {option!r}")
        if option != "hide":
            page.append(f"```python\n{code}\n```")
        if option == "norun":
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            value = run(code, scope)
        if isinstance(value, Table):
            page.append(("\n\n" if option != "hide" else "") + table_markdown(value))
        elif isinstance(value, GC):
            count += 1
            spec = value.to_spec()
            r_file = charts / f"article-{name}-{count}.json"
            r_chart = json.loads(r_file.read_text(encoding="utf-8")) if r_file.exists() else None
            found = check.differences(r_chart["spec"], spec) if r_chart else None
            if found == []:
                same += 1
                chart_id = f"article-{name}-{count}"
            else:
                chart_id = f"python-article-{name}-{count}"
                height = spec.get("height", "400px")
                record = {"id": chart_id, "language": "python", "code": code,
                          "height": height if isinstance(height, str) else f"{height}px", "spec": spec}
                out = json.dumps(record, allow_nan=False)
                if str(tutorials) in out:
                    sys.exit(f"{name}: chart {count} holds the path of the data")
                (charts / f"{chart_id}.json").write_text(out + "\n", encoding="utf-8")
                where = "no R chart of that number" if found is None else f"{len(found)} differences from R, e.g. {found[0][0]}"
                print(f"  {chart_id}: its own file ({where})")
            page.append(f"\n\n@chart {chart_id} nocode")
    pages.mkdir(parents=True, exist_ok=True)
    result = re.sub(r"\n{3,}", "\n\n", "".join(page)).strip() + "\n"
    if str(tutorials) in result:
        sys.exit(f"{name}: the page holds the path of the data")
    (pages / f"{name}.md").write_text(result, encoding="utf-8")
    print(f"{name}: {count} charts, {same} the same as the R article's")


names = sys.argv[1:] or sorted(p.stem for p in sources.glob("*.md"))
for article in names:
    export(article)
