(
    GC(
        ophA_clusters,
        group="class",
        cluster="cluster",
        style={"backgroundColor": "red"},
        height="300px",
    )
    .title(
        "Adjusting Margins of a GC_chart",
        align="left",
        y=15,
        style={"backgroundColor": "yellow", "align": "left"},
    )
    .cluster(style={"backgroundColor": "green"})
    .legend(True, style={"backgroundColor": "yellow"})
    .grid(margin={"top": 50, "bottom": 50, "left": 25, "right": 25})
)
