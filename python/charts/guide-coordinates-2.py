(
    GC(dbophA_cluster, group="class", height="100px")
    .scale(hidden=True, reverse=True)
    .coordinates(
        tick_style={"stroke": "grey", "strokeWidth": 1, "lineLength": 10},
        text_style={
            "fill": "gray",
            "fontSize": "10px",
            "fontFamily": "Arial",
            "cursor": "default",
        },
    )
    .legend(False)
)
