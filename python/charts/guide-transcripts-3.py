GC(transcript_data, height="200px").transcript(
    style_introns={"strokeWidth": 2, "markerHeight": 60},
    style_exons={
        "markerSize": "small",
        "fill": "none",
        "strokeWidth": 2,
        "stroke": "red",
    },
    style_utrs={"marker": "boxarrow", "markerSize": "small", "fill": "green"},
    label_options={
        "show": True,
        "xOffset": 0,
        "yOffset": 0,
        "fontSize": "10px",
        "fontWeight": "bold",
    },
)
