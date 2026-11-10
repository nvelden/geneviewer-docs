import random

ophA_clusters["identity"] = [random.randint(1, 100) for _ in range(len(ophA_clusters))]
ophA_clusters.loc[ophA_clusters["cluster"] == "ophA", "identity"] = None

chart = (
    GC(ophA_clusters, cluster="cluster", group="class", height="250px")
    .links(
        "class",
        value1=["Methyltransferase", "Prolyloligopeptidase"],
        value2=["Methyltransferase", "Prolyloligopeptidase"],
        inverted_color="green",
        measure="identity",
        label=True,
        curve=False,
        color_bar=True,
        color_bar_options={
            "x": 0,
            "y": 24,
            "width": 10,
            "height": 60,
            "labelOptions": {"fontSize": 8, "xOffset": 2, "yOffset": 0},
            "titleOptions": {"fontSize": 10, "xOffset": 2, "yOffset": 0},
            "barOptions": {"stroke": "#000", "strokeWidth": 0.5, "opacity": 1},
        },
        link_width=0.5,
        link_style={"stroke": "black", "strokeWidth": 0.5},
        label_style={"fill": "red"},
    )
    .legend(True)
)

chart
