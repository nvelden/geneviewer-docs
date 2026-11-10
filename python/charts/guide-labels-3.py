(
    GC(ophA_clusters, group="class", cluster="cluster", height="360px")
    .labels("name", y=20)
    .labels(
        "name",
        cluster=2,
        y=20,
        item_style=[
            {"index": 3, "y": 52, "fill": "red"},
            {"index": 7, "y": 52, "fill": "red"},
        ],
    )
)
