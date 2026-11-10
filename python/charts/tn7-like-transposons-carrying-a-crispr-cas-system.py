from geneviewer import GC, datasets

# The element ends are single positions in the data. They are drawn as tall
# bars, the way the inverted repeats at the ends of a transposon are often
# drawn: 100 bp wide, from the end into the element, so they stay clear of the
# gene next to them.
genes = datasets.load("tn7_crispr_elements")
genes.loc[genes["gene"] == "R", "end"] += 100
genes.loc[genes["gene"] == "L", "start"] -= 100

elements = genes[["cluster", "strain_short"]].drop_duplicates()

colors = {
    "insertion site": "#F3C79B",
    "tnsA": "#D62728",
    "tnsB": "#AEB6F0",
    "tnsC": "#D7F2F2",
    "tniQ / tnsD": "#2CA02C",
    "tnsE": "#C7E02C",
    "cas8f / cas5f": "#8C1515",
    "cas7f": "#F2A5C4",
    "cas6f": "#7B3FD4",
    "cas5": "#B5651D",
    "cas, other": "#C9A0DC",
    "CRISPR array": "#555555",
    "right end": "#9FD4DE",
    "left end": "#F28E2B",
    "other": "#E8E8E8",
}

# In the legend the gene names are italic, the other entries upright
gene_names = [
    "tnsA",
    "tnsB",
    "tnsC",
    "tniQ / tnsD",
    "tnsE",
    "cas8f / cas5f",
    "cas7f",
    "cas6f",
    "cas5",
]

legend_styles = {name: {"fontStyle": "italic"} for name in gene_names}

# The labels by their text: white on the dark genes, and above the SRP RNA
# genes, which are too short for it, ending clear of the right end beside them
white = {"fill": "white"}

label_styles = {
    "tnsA": white,
    "cas8f": white,
    "cas6f": white,
    "cas5": white,
    "SRP-RNA": {"y": 55, "dy": "0px", "textAnchor": "end", "x": -4},
}

# By gene: the ends (R and L) are tall bars, the CRISPR arrays and the fused
# tnsA boxes the height of the genes
end_bar = {"marker": "box", "markerHeight": 38, "arrowheadHeight": 38}

gene_box = {"marker": "box", "markerHeight": 20, "arrowheadHeight": 20}

shapes = {
    "R": end_bar,
    "L": end_bar,
    "CRISPR": {**gene_box, "stroke": "black", "strokeWidth": 1},
    "tnsA (fused)": gene_box,
}

chart = (
    GC(genes, cluster="cluster", group="category", strand="strand", height="900px")
    # tall arrows, with the labels inside them
    .genes(marker_size="small", marker_height=20, style_by="gene", group_style=shapes)
    .labels(
        label="label",
        font_size="9px",
        y=50,
        dy="14.5px",
        adjust_labels=False,
        style_by="label",
        group_style=label_styles,
    )
    # most elements run on far beyond the genes shown, up to ~100 kb: scale breaks
    # (//) leave out such long stretches, as in the published figure
    .scale(
        axis_type="range", hidden=True, scale_breaks=True, scale_break_padding="500bp"
    )
    # line the elements up on their right end, as in the published figure
    .align("gene", "R", align="left")
    .cluster_label(
        title=list(elements["cluster"]),
        subtitle=list(elements["strain_short"]),
        width="190px",
        font_size="12px",
        subtitle_font={"fontSize": "10px", "fontStyle": "italic"},
        align="right",
        x=-10,
    )
    .title(
        "Tn7-like transposons that carry a minimal CRISPR-Cas system",
        subtitle="Redrawn from Fig. 3 of Peters et al. (2017), Proc Natl Acad Sci USA 114:E7358-E7366",
        height="70px",
        title_font={"fontSize": "19px", "fontWeight": "bold"},
        subtitle_font={"fontSize": "14px", "fontStyle": "italic"},
    )
    .tooltip(formatter="<b>{gene}</b> {product}<br>{start} - {end}")
    .color(custom_colors=colors)
    # the two ends share a pattern and are told apart by their colour
    .pattern(
        patterns={"right end": "diagonal", "left end": "diagonal"},
        background=None,
        size=4,
    )
    .legend(
        position="bottom",
        align="center",
        order=list(colors),
        legend_text_options={"fontSize": "12px"},
        group_style=legend_styles,
    )
    .theme("publication")
)

chart
