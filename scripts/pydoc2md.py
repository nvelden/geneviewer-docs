"""The Python reference of the docs site: docstrings to Markdown.

Usage: python3 pydoc2md.py <geneviewer-py checkout> <out dir> <index json>

Reads the sources without importing them (the standard library only), so the
build needs no Python packages. The pages are the public names of the package:
``__all__`` of ``geneviewer``, ``geneviewer.shiny`` and ``geneviewer.datasets``,
and the public methods of ``GC``. Also writes the pages made from the package's
``docs/NAMING.md`` and ``docs/differences.md``, next to the out dir.

Fails if a page would lose content: a public name without a docstring, or a
docstring section it does not know.
"""

import ast
import json
import re
import sys
from pathlib import Path

repo, out, manifest = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
package = repo / "src" / "geneviewer"
out.mkdir(parents=True, exist_ok=True)

SECTIONS = ("Parameters", "Returns", "Raises", "Examples", "Notes", "See Also")
# Sidebar groups, by the module a name is defined in
GROUPS = (
    ("Chart", ("chart",)),
    ("Shiny", ("shiny",)),
    ("Files", ("readers", "processing")),
    ("Alignment", ("align",)),
    ("Themes", ("theme",)),
    ("Datasets", ("datasets",)),
)


def all_names(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit(f"{path}: no __all__")


# Every top-level function and class of the package, by name
definitions = {}
for path in sorted(package.rglob("*.py")):
    module = ".".join(path.relative_to(package).with_suffix("").parts)
    module = re.sub(r"\.?__init__$", "", module)
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                definitions.setdefault(node.name, (module, node))

pages = []  # (page, title, call, module, node, is_class)
for name in all_names(package / "__init__.py"):
    if name in ("__version__", "datasets"):
        continue
    module, node = definitions[name]
    if isinstance(node, ast.ClassDef):
        pages.append((name, f"{name}()", name, module, node, True))
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                pages.append((f"{name}-{item.name}", f"{name}.{item.name}()",
                              f"chart.{item.name}", module, item, False))
    else:
        pages.append((name, f"{name}()", name, module, node, False))
for sub in ("shiny", "datasets"):
    path = package / f"{sub}.py"
    path = path if path.exists() else package / sub / "__init__.py"
    for name in all_names(path):
        if name.isupper():
            continue  # a constant, described where it is used
        module, node = definitions[name]
        prefix = "datasets." if sub == "datasets" else ""
        page = f"datasets-{name}" if sub == "datasets" else name
        pages.append((page, f"{prefix}{name}()", f"{prefix}{name}", sub, node,
                      isinstance(node, ast.ClassDef)))

links = {}
for page, title, call, *_ in pages:
    links[title[:-2]] = page
    links[title[:-2].split(".")[-1]] = links.get(title[:-2].split(".")[-1], page)
links["GC"] = "GC"


def escape(text):
    text = text.replace("\\", "\\\\").replace("<", "&lt;").replace("{{", "&#123;&#123;")
    return re.sub(r"([*_\[])", r"\\\1", text)


def inline(text, cell=False):
    """RST inline markup to Markdown: ``code`` and `name` (a link if it has a page)."""
    parts = re.split(r"(``.+?``|`[^`]+`)", text)
    done = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            done.append(escape(part))
            continue
        code = part.strip("`")
        ticks = "``" if "`" in code else "`"
        shown = f"{ticks}{code}{ticks}"
        target = None if part.startswith("``") else links.get(code.rstrip("()"))
        done.append(f"[{shown}](./{target})" if target else shown)
    text = "".join(done)
    return text.replace("|", "\\|") if cell else text


def paragraphs(lines, cell=False):
    """Lines of prose to Markdown paragraphs; indented or doctest lines stay code."""
    blocks, current = [], []
    for line in [*lines, ""]:
        if line.strip():
            current.append(line)
            continue
        if current:
            blocks.append(current)
            current = []
    result = []
    for block in blocks:
        if block[0].lstrip().startswith(">>>"):
            code = "\n".join(line.strip() for line in block)
            result.append(f"<code>{escape(code)}</code>" if cell else f"```python\n{code}\n```")
        elif all(re.match(r"\s*[-*] ", line) or line.startswith("  ") for line in block):
            items = re.split(r"\n\s*[-*] ", "\n" + "\n".join(block))[1:]
            texts = [inline(" ".join(item.split()), cell) for item in items]
            result.append("<br>".join(f"• {t}" for t in texts) if cell
                          else "\n".join(f"- {t}" for t in texts))
        else:
            result.append(inline(" ".join(" ".join(block).split()), cell))
    return ("<br><br>" if cell else "\n\n").join(result)


def split_sections(doc, where):
    lines = doc.splitlines()
    sections, name, start = {}, "", 0
    for i, line in enumerate(lines):
        if i + 1 < len(lines) and re.fullmatch(r"-{3,}", lines[i + 1].strip()) and line.strip():
            if line.strip() not in SECTIONS:
                raise SystemExit(f"{where}: unknown docstring section {line.strip()!r}")
            sections[name] = lines[start:i]
            name, start = line.strip(), i + 2
    sections[name] = lines[start:]
    return sections


def entries(lines):
    """The entries of a Parameters, Returns or Raises section: (head, body lines)."""
    found = []
    for line in lines:
        if line.strip() and not line.startswith(" "):
            found.append((line.strip(), []))
        elif found:
            found[-1][1].append(line[4:] if line.startswith("    ") else line.strip())
    return found


def signature(call, node, is_class):
    if is_class:
        init = [n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"]
        if not init:
            return f"@{call}"  # a decorator class, such as a Shiny renderer
        node = init[0]
    a = node.args
    names = [*a.posonlyargs, *a.args]
    defaults = [None] * (len(names) - len(a.defaults)) + list(a.defaults)
    shown = []
    for arg, default in zip(names, defaults):
        if arg.arg in ("self", "cls"):
            continue
        value = None if default is None else ast.unparse(default)
        # _MISSING: the argument was not given, and the library's default applies
        shown.append(arg.arg if value in (None, "_MISSING") else f"{arg.arg}={value}")
    if a.vararg:
        shown.append(f"*{a.vararg.arg}")
    for arg, default in zip(a.kwonlyargs, a.kw_defaults):
        value = None if default is None else ast.unparse(default)
        shown.append(arg.arg if value in (None, "_MISSING") else f"{arg.arg}={value}")
    if a.kwarg:
        shown.append(f"**{a.kwarg.arg}")
    flat = f"{call}({', '.join(shown)})"
    if len(flat) <= 80:
        return flat
    return f"{call}(\n" + "".join(f"    {s},\n" for s in shown) + ")"


def table(lines, first):
    rows = [f"| {first} | Type | Description |", "| --- | --- | --- |"]
    for head, body in entries(lines):
        name, _, kind = head.partition(" : ")
        names = ", ".join(f"`{n.strip()}`" for n in name.split(","))
        rows.append(f"| {names} | {inline(kind, True)} | {paragraphs(body, True)} |")
    return "\n".join(rows)


def page_markdown(page, title, call, module, node, is_class):
    doc = ast.get_docstring(node)
    if not doc:
        raise SystemExit(f"{title}: no docstring")
    sections = split_sections(doc, title)
    intro = sections[""]
    summary = intro[0].strip()
    parts = [f"# `{title[:-2]}()`" if not is_class or title != "GC()" else "# `GC()`",
             inline(summary)]
    rest = paragraphs(intro[1:])
    if rest:
        parts.append(rest)
    where = "geneviewer" if module in ("chart", "theme", "processing") or module.startswith(("readers", "align")) else f"geneviewer.{module}"
    imported = call.split(".")[0] if not call.startswith("chart.") else None
    usage = signature(call, node, is_class)
    if imported == "datasets":
        usage = f"from geneviewer import datasets\n\n{usage}"
    elif imported:
        usage = f"from {where} import {imported}\n\n{usage}"
    parts.append(f"## Usage\n\n```python\n{usage}\n```")
    if re.search(r"[(\s]\w+[,)]", usage.split("\n\n")[-1]) and "Parameters" in sections:
        parts.append("An argument shown without a default is optional too: "
                     "left out, the chart keeps its default.")
    if call.startswith("chart."):
        parts.append("`chart` is a [`GC`](./GC) chart.")
    if "Parameters" in sections:
        parts.append("## Arguments\n\n" + table(sections["Parameters"], "Argument"))
    if "Returns" in sections:
        found = entries(sections["Returns"])
        text = "\n\n".join(f"{inline(head)}: {paragraphs(body)}" if body else inline(head)
                           for head, body in found)
        parts.append("## Value\n\n" + text)
    if "Raises" in sections:
        rows = ["| Error | When |", "| --- | --- |"]
        rows += [f"| `{head}` | {paragraphs(body, True)} |" for head, body in entries(sections["Raises"])]
        parts.append("## Errors\n\n" + "\n".join(rows))
    if "Notes" in sections:
        parts.append("## Details\n\n" + paragraphs(sections["Notes"]))
    if "Examples" in sections:
        code = "\n".join(sections["Examples"]).strip("\n")
        parts.append(f"## Examples\n\n```python\n{code}\n```")
    if "See Also" in sections:
        parts.append("## See also\n\n" + paragraphs(sections["See Also"]))
    return summary, "\n\n".join(parts) + "\n"


index = []
for entry in pages:
    page, title, call, module, node, is_class = entry
    summary, text = page_markdown(*entry)
    (out / f"{page}.md").write_text(text, encoding="utf-8")
    group = next(g for g, modules in GROUPS if module.split(".")[0] in modules)
    index.append({"page": page, "title": title, "group": group, "summary": summary})

datasets = json.loads((package / "datasets" / "datasets.json").read_text(encoding="utf-8"))
lines = ["---", "prev: false", "next: false", "---", "", "# Python reference", "",
         "Every function and method of the Python package, and its datasets."]
for group, _ in GROUPS:
    lines += ["", f"## {group}", "", "| | |", "| --- | --- |"]
    lines += [f"| [`{e['title']}`](./{e['page']}) | {inline(e['summary'].rstrip('.'), True)} |"
              for e in index if e["group"] == group]
    if group == "Datasets":
        lines += ["", "The datasets are those of the R package; "
                  "`datasets.load(name)` returns one as a pandas DataFrame.", "",
                  "| Dataset | Rows | Columns | |", "| --- | --- | --- | --- |"]
        lines += [f"| `{name}` | {d['rows']} | {len(d['columns'])} | {escape(d['title'])} |"
                  for name, d in datasets.items()]
(out / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
manifest.write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")


def repo_page(source, target, title_from, links_to):
    """A Markdown file of the package as a page of the site."""
    text = (repo / source).read_text(encoding="utf-8")
    text = re.sub(r"^# .*$", f"# {title_from}", text, count=1, flags=re.M)
    for name, link in links_to.items():
        text = text.replace(f"`{name}`", f"[`{name}`]({link})")
    text = text.replace("{{", "&#123;&#123;")
    (out.parent / target).write_text(
        f"<!-- Made by scripts/pydoc2md.py from {source} of geneviewer-py. Edit that. -->\n\n{text}",
        encoding="utf-8")


repo_page("docs/NAMING.md", "naming.md", "Names in Python and R",
          {"docs/differences.md": "./differences"})
repo_page("docs/differences.md", "differences.md", "Differences from the R package", {})
print(f"python reference: {len(index)} pages")
