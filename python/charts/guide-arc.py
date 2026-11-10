transcript_data = pd.DataFrame(
    {
        "transcript": ["transcript1", "transcript1", "transcript1", "transcript1"],
        "type": ["5_utr", "exon", "exon", "3_utr"],
        "start": [1, 101, 201, 301],
        "end": [50, 150, 250, 350],
        "strand": ["forward"] * 4,
    }
)

(
    GC(transcript_data, start="start", end="end", height="200px")
    .transcript(transcript="transcript", strand="strand")
    .annotation(
        cluster=None,
        type="arc",
        x1=[150, 50],
        y1=[50],
        x2=[301, 201],
        y2=[50],
        mid_y=[80, 20],
        stroke=["black"],
        stroke_width=[0.8, 0.1],
        label_x=[0],
        label_y=[0],
        text=[0.8, 0.1],
        line_style={},
        text_style={
            "fontSize": "10px",
            "fontFamily": "sans-serif",
            "fill": "black",
            "textAnchor": "middle",
        },
    )
    .legend(False)
    .track_mouse()
)
