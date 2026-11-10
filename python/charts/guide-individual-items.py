(
    GC(ophA_clusters, cluster="cluster", group="class", height="300px")
    .title(title="ophA Gene Clusters", height="30px")
    .labels(
        label="name",
        cluster="ophA",
        item_style=[{"index": 2, "fill": "red", "fontWeight": "bold"}],
    )
    .labels(
        label="name",
        cluster=2,
        item_style=[
            {"index": 4, "fill": "red", "fontWeight": "bold"},
            {"index": 3, "y": 10, "x": -5},
        ],
    )
)
