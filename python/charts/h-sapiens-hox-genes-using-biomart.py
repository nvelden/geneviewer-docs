from geneviewer import GC, datasets

# The positions of the HOX genes, from Ensembl
human_hox_genes = datasets.load("human_hox_genes")

(
    GC(
        human_hox_genes,
        group="cluster",
        strand="strand",
        cluster="cluster",
        height="400px",
    )
    .cluster_label()
    .legend(False)
    .genes(marker="boxarrow", marker_height=10, arrowhead_height=10, arrowhead_width=6)
    .labels("name", font_size="10px")
    .scale(cluster=[1, 2], hidden=True, reverse=True)
    .cluster(prevent_gene_overlap=True)
    .theme("dark")
)
