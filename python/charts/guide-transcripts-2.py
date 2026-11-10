GC(transcript_data, start="start", end="end", height="200px").transcript(
    group="type",
    custom_colors={
        "exon": "green",
        "intron": "blue",
        "5_utr": "black",
        "3_utr": "grey",
    },
)
