(
    GC(ophA_clusters, cluster="cluster", group="class", height="300px")
    .labels("name")
    .coordinates()
    .cluster_label(title=["O. olearius", "D. bispora"], subtitle="ophA")
    .element_style("genes", row_id=3, fill="red", marker_height=30)
    .element_style("labels", row_id=3, text="ophMA", font_weight="bold")
    .element_style("coordinates", row_id=1, end="start", show=False)
    .element_style(
        "clusterLabel", cluster=2, part="subtitle", text="dbophA", fill="grey"
    )
)
