from geneviewer import GC, datasets

# Rotate each circular genome to start at COX1, preserving genomic spacing,
# and label reverse-strand genes with a leading minus, as in the published
# figure. The original coordinates are kept for the tooltips.
genes = datasets.load("mitochondrial_gene_order")
cox1_start = genes[genes["gene"] == "COX1"].set_index("cluster")["start"]
genes["genomic_start"] = genes["start"]
genes["genomic_end"] = genes["end"]
genes["plot_start"] = (genes["start"] - genes["cluster"].map(cox1_start)) % genes[
    "genome_length"
] + 1
genes["plot_end"] = genes["plot_start"] + genes["end"] - genes["start"]
genes["label"] = [
    "-" + gene if strand == "complement" else gene
    for gene, strand in zip(genes["gene"], genes["strand"])
]

genomes = genes[["cluster", "genome_length"]].drop_duplicates()

colors = {
    "Conserved flanks": "#D9D5D2",
    "ND4L / ND4 / ND5": "#F22228",
    "ND6": "#FFF000",
    "CYTB": "#00AC52",
    "RNS / RNL / ND1": "#36328C",
}

chart = (
    GC(
        genes,
        start="plot_start",
        end="plot_end",
        cluster="cluster",
        group="block",
        strand="strand",
        height="320px",
    )
    .genes(marker="box", marker_height=18, arrowhead_height=18, corner_radius=0)
    # A negative spacing puts reverse-strand genes above the baseline and
    # forward-strand genes below it, as in the published figure.
    .cluster(separate_strands=True, strand_spacing=-18)
    # The labels go on one line below the genes, with a line to each gene
    .labels(
        "label", font_style="normal", adjust_labels="spread", leader_line={"length": 12}
    )
    .color(custom_colors=colors)
    .scale(axis_type="range", hidden=True)
    .grid(margin={"top": 0, "bottom": 0})
    .cluster_footer(
        title=list(genomes["cluster"]),
        subtitle=[
            f"13 proteins; 2 rRNAs; {length:,} bp"
            for length in genomes["genome_length"]
        ],
        align="left",
        y=10,
    )
    .title(
        "Mitochondrial gene order: locust and human",
        subtitle="Redrawn from Fig. 3 of Jameson et al. (2003), Nucleic Acids Res 31:202-206",
        title_font={"fontSize": "19px"},
    )
    .tooltip(
        formatter="<b>{gene}</b>: {product}<br>{cluster}<br>RefSeq: {accession}<br>Original coordinates: {genomic_start} - {genomic_end} ({strand})"
    )
    .legend(False)
    .theme("publication", font_family="Courier New, Courier, monospace")
)

chart
