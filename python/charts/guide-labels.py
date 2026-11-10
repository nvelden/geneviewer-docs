(
    GC(
        ophA_clusters,
        start="start",
        end="end",
        group="class",
        cluster="cluster",
        height="450px",
    )
    .cluster_title(
        title=["<i>Omphalotus Olearius</i>", "<i>Dendrothele Bisporus</i>"],
        title_font={"fontWeight": "normal"},
    )
    .labels("name")
    .cluster_label(title=list(ophA_clusters["cluster"].unique()))
    .cluster_footer(
        title=["Nr. of Genes: 7", "Nr. of Genes: 10"],
        subtitle=["Locus: 2522 - 21,484", "Locus 19,236 - 43,005"],
    )
    .legend(position="top")
)
