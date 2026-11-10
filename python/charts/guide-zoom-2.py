(
    GC(ophA_clusters, cluster="cluster", group="class", height="300px")
    .labels("name")
    .scale(hidden=False)
    .zoom(
        mode="absolute",
        range=[10000, 20000],
        update="release",
        height=30,
        handle_style={"backgroundColor": "#d9d9d9"},
    )
)
