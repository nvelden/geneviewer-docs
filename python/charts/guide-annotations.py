(
    GC(ophA_clusters, group="class", cluster="cluster", height="300px")
    .annotation(cluster=1, type="text", text="Gene 1", x=2970, y=60)
    .annotation(
        cluster=2,
        type="text",
        text=["Gene 1", "Gene 2", "Gene 3"],
        x=[19400, 22200, 25600],
        y=60,
    )
    .legend(False)
    .track_mouse()
)
