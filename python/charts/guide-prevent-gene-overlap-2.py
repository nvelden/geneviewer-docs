nested = {"markerHeight": 8, "arrowheadHeight": 8}

(
    GC(
        coronavirus_genomes[coronavirus_genomes["cluster"] == "SARS-CoV-2"],
        group="category",
        cluster="cluster",
        height="380px",
    )
    .cluster(prevent_gene_overlap="nested", overlap_spacing=20)
    .genes(style_by="geneTrack", group_style={"2": nested, "3": nested})
    .labels("gene")
    .zoom(range=[0.83, 1])
)
