(
    GC(ophA_clusters, group="class", cluster="cluster", height="150px")
    .scale_bar(
        title="1kb",
        scale_bar_unit=1000,
        cluster=None,
        x=0,
        y=0,
        label_style={
            "labelPosition": "left",
            "fontSize": "10px",
            "fontFamily": "sans-serif",
            "fill": "black",
            "cursor": "default",
        },
        text_padding=2,
        scale_bar_line_style={"stroke": "black", "strokeWidth": 1},
        scale_bar_tick_style={"stroke": "black", "strokeWidth": 1},
    )
    .legend(y=10)
)
