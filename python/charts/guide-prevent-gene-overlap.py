(
    GC(
        human_hox_genes[human_hox_genes["cluster"].isin(["HOXA", "HOXB"])],
        group="name",
        cluster="cluster",
        height="390px",
    )
    .labels(label="name", adjust_labels=False)
    .labels(label="name", cluster=2, item_style=[{"index": 5, "x": 10}])
    .cluster(prevent_gene_overlap=True, overlap_spacing=30)
    .legend(False)
)
