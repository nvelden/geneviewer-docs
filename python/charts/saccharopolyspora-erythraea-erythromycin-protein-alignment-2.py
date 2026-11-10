from geneviewer import GC, datasets

# Genes without a hit have no function: give them their own group
blastp = datasets.load("erythromycin_BlastP")
blastp = blastp[blastp["cluster"].isin(["BGC0000055", "BGC0000054"])]
blastp["Functions"] = blastp["Functions"].fillna("No Hit")

(
    GC(blastp, cluster="cluster", strand="strand", group="Functions", height=250)
    .labels("Gene", cluster=1)
    .genes(
        marker_size="small",
        marker="rbox",
        marker_height=15,
        stroke="#6E7079",
        stroke_width=0.5,
    )
    .links(group="BlastP", label=False, color_bar=False)
    .cluster_label()
    .legend(False)
    .color(custom_colors={"No Hit": "white"})
    .theme("classic", text_color="#333333", palette="okabeIto")
)
