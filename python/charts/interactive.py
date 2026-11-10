from geneviewer import GC, datasets

ophA_clusters = datasets.load("ophA_clusters")

(
    GC(ophA_clusters, group="class", cluster="cluster", height="320px")
    .labels("name")
    .links("class", measure="identity")
    .cluster_label()
    .zoom()
    .events(select=True)
)
