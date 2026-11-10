"""The charts of the Python pages: run each snippet, record its spec.

Usage, with geneviewer-py installed (``pip install "geneviewer-py[align]"``)
and GENEVIEWER_PY_DIR set to a checkout of it (for the GenBank example file):

    python scripts/export-python-charts.py

Writes site/public/charts/python-<name>.json: the code as the page shows it
and the spec it made. Both are committed, so the code on a page is the code
that ran. A page shows a chart with ``@chart python-<name>``.

Each snippet ends with a chart named ``chart``. ``setup`` runs before it and
is not shown (the page shows it in its text).
"""

import json
import os
import re
import textwrap
from pathlib import Path

py_dir = Path(os.environ["GENEVIEWER_PY_DIR"])
gbk = py_dir / "tests" / "readers" / "inputs" / "BGC0000001.gbk"
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

chart("genbank", f"""
    from geneviewer import GC

    chart = GC("BGC0000001.gbk", height="150px").labels("protein_id")
""".replace("BGC0000001.gbk", str(gbk)))

chart("genbank-features", """
    chart = (
        GC(cds, group="gene_kind", height="180px")
        .genes(marker="boxarrow", marker_size="small")
        .scale()
        .tooltip(formatter="<b>{gene}</b><br>{product}<br>{start} - {end}")
        .legend(position="bottom")
    )
""", setup=f"""
    import geneviewer as gv
    from geneviewer import GC
    records = gv.read_gbk({str(gbk)!r})
    cds = gv.gbk_features_to_df(
        records, feature="CDS", keys=["region", "gene", "product", "gene_kind"]
    )
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

chart("protein-alignment", """
    chart = (
        GC(hits, cluster="cluster", group="BlastP", strand="strand", height="600px")
        .links(group="BlastP", measure="identity", label=False)
        .cluster_label()
        .legend(False)
    )
""", setup="""
    import geneviewer as gv
    from geneviewer import GC, datasets
    genes = datasets.load("erythromycin_BlastP")[
        ["protein_id", "region", "translation", "cluster", "strand", "start", "end"]
    ]
    hits = gv.protein_blast(genes, query="BGC0000055", identity=30)
    hits = hits.drop(columns="translation")
""")

chart("alignment-links", """
    from geneviewer import GC, datasets

    plasmids = datasets.load("pQEB1_plasmids")
    alignment = datasets.load("pQEB1_alignment")

    chart = (
        GC(plasmids, cluster="cluster", group="category", strand="strand",
           height="600px")
        .links(data=alignment, measure="identity", label=False)
        .genes(marker_size="small")
        .scale(axis_type="range")
        .cluster_label(width="175px", align="right", x=-10)
        .legend(position="top")
    )
""")

for name, (setup, code) in CHARTS.items():
    scope = {}
    exec(setup, scope)
    exec(code, scope)
    spec = scope["chart"].to_spec()
    shown = code.replace(str(gbk), gbk.name)
    height = spec.get("height", "400px")
    record = {"id": f"python-{name}", "language": "python", "code": shown,
              "height": height if isinstance(height, str) else f"{height}px", "spec": spec}
    text = json.dumps(record, indent=1, allow_nan=False)
    assert str(py_dir) not in text and not re.search(r"/Users/", text), name
    (out / f"python-{name}.json").write_text(text + "\n", encoding="utf-8")
    print(f"python-{name}: {len(text) // 1024} kB")
