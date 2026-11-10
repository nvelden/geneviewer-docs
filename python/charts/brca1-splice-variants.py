from geneviewer import GC, datasets

BRCA1_splice_variants = datasets.load("BRCA1_splice_variants")

(
    GC(BRCA1_splice_variants, height="600px")
    .transcript(transcript="ensembl_transcript_id", strand="strand", type="type")
    .cluster_title(
        title=list(BRCA1_splice_variants["ensembl_transcript_id"].unique()),
        title_font={"fontSize": "12px"},
    )
    .cluster_footer(title=["0.8%", "0.1%", "0.07%", "0.02%", "0.01%"], align="center")
    .theme("infographic", text_color="#333333")
)
