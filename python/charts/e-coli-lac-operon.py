import pandas as pd

from geneviewer import GC

lacZ_operon = pd.DataFrame(
    {
        "start": [361249, 361926, 363231, 366428],
        "end": [361860, 363179, 366305, 367510],
        "Gene_symbol": ["lacA", "lacY", "lacZ", "lacI"],
        "Strand": ["minus", "minus", "minus", "minus"],
        "NCBI_Gene_ID": ["945674", "949083", "945006", "945007"],
        "Description": [
            "galactoside O-acetyltransferase",
            "lactose permease",
            "beta-galactosidase",
            "DNA-binding transcriptional repressor LacI",
        ],
    }
)

(
    GC(lacZ_operon, group="Gene_symbol", height="140px")
    .labels()
    .scale_bar(title="0.2 kb", scale_bar_unit=200, y=30)
    .tooltip(
        formatter="\n    <b>ID:</b> {NCBI_Gene_ID}<br>\n    <b>Description:</b> {Description}<br>\n    <b>Start:</b> {start}<br>\n    <b>End:</b> {end}"
    )
    .cluster_footer(
        align="center",
        y=-30,
        subtitle="<i>Escherichia coli</i> str. K-12 substr. MG1655",
    )
    .coordinates(
        rotate=0,
        tick_values_bottom=[lacZ_operon["start"].min(), lacZ_operon["end"].max()],
        text_style={"fontSize": "10px", "x": -2.2, "y": 1.2},
        tick_style={"lineLength": 10},
    )
    .legend(False)
)
