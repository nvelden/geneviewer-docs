# With scale breaks
(
    GC(ophA_cluster, group="class", height="100px")
    .scale(scale_breaks=True, scale_break_threshold=20, scale_break_padding=1)
    .legend(False)
)
