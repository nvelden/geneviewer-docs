transcript_data = pd.DataFrame(
    {
        "transcript": [
            "transcript1",
            "transcript1",
            "transcript1",
            "transcript1",
            "transcript2",
            "transcript2",
            "transcript2",
        ],
        "type": ["5_utr", "exon", "exon", "3_utr", "5_utr", "exon", "3_utr"],
        "start": [1, 101, 201, 301, 1, 101, 301],
        "end": [50, 150, 250, 350, 50, 150, 350],
        "strand": ["forward"] * 7,
    }
)

GC(transcript_data, start="start", end="end", height="200px").transcript(
    transcript="transcript", strand="strand"
)
