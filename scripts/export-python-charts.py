"""The charts of the Python pages: run each snippet, record its spec.

Usage, with geneviewer-py installed:

    python scripts/export-python-charts.py

Writes site/public/charts/python-<name>.json: the code as the page shows it
and the spec it made. Both are committed, so the code on a page is the code
that ran. A page shows a chart with ``@chart python-<name>``.

Each snippet ends with a chart named ``chart``. ``setup`` runs before it and
is not shown (the page shows it in its text).
"""

import json
import re
import textwrap
from pathlib import Path

out = Path(__file__).resolve().parents[1] / "site" / "public" / "charts"

CHARTS = {}


def chart(name, code, setup=""):
    CHARTS[name] = (textwrap.dedent(setup).strip(), textwrap.dedent(code).strip())


chart("first-chart", """
    from geneviewer import GC, datasets

    clusters = datasets.load("ophA_clusters")
    ophA = clusters[clusters["cluster"] == "ophA"]

    chart = GC(ophA, group="class", height="150px")
""")

chart("methods", """
    chart = (
        GC(clusters, cluster="cluster", group="class", height="300px")
        .title("Omphalotin gene clusters", height="40px")
        .labels("name")
        .links(group="class", label=False)
        .cluster_label(["<i>O. olearius</i>", "<i>D. bispora</i>"])
        .scale_bar()
        .legend(position="bottom")
    )
""", setup="""
    from geneviewer import GC, datasets
    clusters = datasets.load("ophA_clusters")
""")

chart("theme", """
    chart = (
        GC(clusters, cluster="cluster", group="class", height="260px")
        .labels("name", font_size="11px")
        .genes(marker="boxarrow", marker_size="small")
        .theme("vintage")
    )
""", setup="""
    from geneviewer import GC, datasets
    clusters = datasets.load("ophA_clusters")
""")

chart("transcripts", """
    from geneviewer import GC, datasets

    transcripts = datasets.load("BRCA1_splice_variants")

    chart = (
        GC(transcripts, height="450px")
        .transcript(transcript="ensembl_transcript_id", strand="strand", type="type")
        .cluster_title(
            list(transcripts["ensembl_transcript_id"].unique()),
            title_font={"fontSize": "12px"},
        )
    )
""")

chart("jupyter-widget", """
    widget = (
        GC(clusters, cluster="cluster", group="class", height="300px")
        .labels("name")
        .zoom()
        .events(select=True, drag=True, zoom=True)
        .widget()
    )
    widget
""", setup="""
    from geneviewer import GC, datasets
    clusters = datasets.load("ophA_clusters")
""")

for name, (setup, code) in CHARTS.items():
    scope = {}
    exec(setup, scope)
    exec(code, scope)
    # A snippet for a notebook ends with its widget
    spec = (scope["chart"] if "chart" in scope else scope["widget"].chart).to_spec()
    shown = code
    height = spec.get("height", "400px")
    record = {"id": f"python-{name}", "language": "python", "code": shown,
              "height": height if isinstance(height, str) else f"{height}px", "spec": spec}
    text = json.dumps(record, indent=1, allow_nan=False)
    assert not re.search(r"/Users/", text), name
    (out / f"python-{name}.json").write_text(text + "\n", encoding="utf-8")
    print(f"python-{name}: {len(text) // 1024} kB")
