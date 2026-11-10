(
    GC(transcript_data, start="start", end="end", height="200px")
    .transcript(
        transcript="transcript",
        selection=1,
        item_style_exons=[{"index": 0, "fill": "red"}],
    )
    .transcript(
        transcript="transcript",
        selection=2,
        item_style_introns=[{"index": 1, "stroke": "red", "strokeWidth": 2}],
    )
)
