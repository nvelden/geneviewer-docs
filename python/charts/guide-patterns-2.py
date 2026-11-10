all_patterns = [
    "diagonal",
    "dots",
    "horizontal",
    "crosshatch",
    "vertical",
    "zigzag",
    "checkerboard",
    "solid",
    "rings",
    "bricks",
    "inverseDots",
    "grid",
    "wideStripes",
    "plus",
    "antidiagonal",
    "none",
]

# Two rows of 8 genes
pattern_genes = pd.DataFrame(
    {
        "start": [100 * i for i in range(8)] * 2,
        "end": [100 * i + 85 for i in range(8)] * 2,
        "pattern": all_patterns,
        "row": ["1"] * 8 + ["2"] * 8,
    }
)

(
    GC(pattern_genes, group="pattern", cluster="row", height="260px")
    .labels("pattern", font_size="11px")
    .legend(order=all_patterns)
    .pattern(patterns=dict(zip(all_patterns, all_patterns)))
)
