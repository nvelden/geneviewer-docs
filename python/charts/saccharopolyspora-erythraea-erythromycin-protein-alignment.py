from geneviewer import GC, datasets

# Genes without a hit have no function: give them their own group
blastp = datasets.load("erythromycin_BlastP")
blastp["Functions"] = blastp["Functions"].fillna("No Hit")

(
    GC(blastp, cluster="cluster", strand="strand", group="Functions", height=700)
    .title(title="Protein Alignment Results")
    .labels("Gene", cluster=1)
    .links(
        group="Gene",
        show_links=False,
        color_bar=False,
        label_style={"fontSize": "10px"},
    )
    .cluster_label()
    .genes(stroke="#6E7079", stroke_width=0.5)
    .legend(order=[*sorted(set(blastp["Functions"]) - {"No Hit"}), "No Hit"])
    .color(custom_colors={"No Hit": "white"})
    .theme("infographic", text_color="#333333", palette="okabeIto")
)
