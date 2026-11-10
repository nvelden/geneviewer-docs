from geneviewer import GC, datasets

erythromycin_cluster = datasets.load("erythromycin_cluster")

(
    GC(
        erythromycin_cluster,
        start="Start",
        end="End",
        group="Functions",
        height="170px",
    )
    .title(
        title="Erythromycin A biosynthetic gene cluster from <i>Saccharopolyspora erythraea</i>",
        align="left",
    )
    .genes(marker="boxarrow", marker_size="small")
    .tooltip(formatter="<b>{Identifiers}</b><br>{Product}<br>{start} - {end}({Strand})")
    .scale(start=778000, end=832000, ticks_count=8)
    .legend(
        order=[*sorted(set(erythromycin_cluster["Functions"]) - {"Other"}), "Other"]
    )
    .color(custom_colors={"Other": "grey"})
    .theme("classic")
)
