(
    GC(ophA_clusters, group="class", cluster="cluster", height="360px")
    .cluster_title(
        ["<i>Omphalotus Olearius</i>", "<i>Dendrothele Bisporus</i>"],
        position="left",
        x=20,
    )
    .labels("name", y=20)
    .labels(
        "name",
        cluster=2,
        y=20,
        item_style=[{"index": 3, "y": 52}, {"index": 7, "y": 52}],
    )
    .cluster_footer(
        title=["Nr. of Genes: 7", "Nr. of Genes: 10"],
        subtitle=["Locus: 2522 - 21,484", "Locus 19,236 - 43,005"],
        align="center",
    )
)
