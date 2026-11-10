(
    GC(ophA_cluster, group="class", height="100px")
    .scale(
        ticks_format=".2s",
        tick_values=[*ophA_cluster["start"], *ophA_cluster["end"]],
        tick_style={"stroke": "black", "strokeWidth": 2, "lineLength": 12},
        text_style={"y": 15, "fill": "black", "fontSize": "8px", "fontFamily": "Arial"},
        line_style={"stroke": "black", "strokeWidth": 2},
    )
    .legend(False)
)
