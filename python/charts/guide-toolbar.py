(
    GC(ophA_cluster, group="class", height="180px")
    .labels("name")
    .events(select=True, drag=True)
    .toolbar(
        show="always",
        position="topleft",
        size=16,
        color="#9e9e9e",
        hover_color="#1f77b4",
        tooltip_background="#1f77b4",
        icons={
            "undo": "arrow-left",
            "redo": "arrow-right",
            "reset": "arrows-to-circle",
            "save": "camera",
        },
    )
)
