dbophA_cluster = ophA_clusters[ophA_clusters["cluster"] == "dbophA"]

(
    GC(dbophA_cluster, group="class", height="100px")
    .coordinates(
        rotate=-45, y_position_top=55, y_position_bottom=45, overlap_threshold=20
    )
    .legend(False)
)
