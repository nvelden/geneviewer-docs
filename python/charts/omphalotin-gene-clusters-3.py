from geneviewer import GC, datasets

ophA_clusters = datasets.load("ophA_clusters")

(
    GC(ophA_clusters, cluster="cluster", group="class", width="800px", height="400px")
    .labels(cluster=1, label="name")
    .links(
        "class",
        use_group_colors=False,
        measure="none",
        normal_color="#969696",
        inverted_color="#969696",
        curve=True,
        label=False,
        link_width=0.2,
    )
    .links(
        group="name",
        value1="ophA",
        value2="dbophA",
        use_group_colors=True,
        link_style={"stroke": "black", "strokeWidth": 2},
    )
    .cluster_label(
        title=["<i>O.</i> <i>olearius</i>", "<i>D. bispora</i>"], wrap_label=False
    )
    # Reduce space between legend and cluster
    .grid(cluster=2, height="25%")
    .legend(legend_text_options={"fontSize": "14px"})
    .annotation(
        cluster=1,
        x=10884,
        y=11,
        type="text",
        text="90%",
        style={"fontSize": "16px", "fill": "#1c641c"},
    )
    .track_mouse()
)
