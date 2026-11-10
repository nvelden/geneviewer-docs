(
    GC(ophA_clusters, cluster="cluster", group="class", height="300px")
    .links(
        data=links_data,
        measure="identity",
        label_position="link",
        color_bar_options={"position": "legend"},
    )
    .legend(position="top")
)
