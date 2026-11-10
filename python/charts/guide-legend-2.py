(
    GC(ophA_clusters, group="class", cluster="cluster", height="200px")
    .legend(
        y=10,
        position="top",
        width="60%",
        order=sorted(ophA_clusters["class"].unique()),
        legend_text_options={"fontSize": "14px"},
        legend_options={"stroke": "black", "strokeWidth": "2px"},
    )
    .color(color_scheme="schemePaired")
)
