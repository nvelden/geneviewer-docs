from geneviewer import GC, datasets

ophA_clusters = datasets.load("ophA_clusters")

(
    GC(ophA_clusters, group="class", cluster="cluster")
    .cluster_footer(
        title=["<i>Omphalotus olearius</i>", "<i>Dendrothele bispora</i>"],
        subtitle=["Locus: 2,522 - 21,484", "Locus: 19,236 - 43,005"],
        align="left",
    )
    .legend(position="top")
    .labels(label="name")
    .scale_bar(y=20)
    .scale(cluster=1, scale_breaks=True, hidden=True)
    .scale(cluster=2, reverse=True, hidden=True)
    .tooltip(
        formatter="<b>Gene:</b> {name}<br> <b>Start:</b> {start}<br><b>end:</b> {end}"
    )
    .theme("vintage")
)
