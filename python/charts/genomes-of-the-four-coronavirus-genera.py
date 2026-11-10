from geneviewer import GC, datasets

coronavirus_genomes = datasets.load("coronavirus_genomes")

genomes = coronavirus_genomes[
    ["cluster", "genus", "subgenus", "host"]
].drop_duplicates()

# Name the genus above its first genome; the others get no title, nor room
# for one
first_of_genus = genomes.drop_duplicates("genus")

colors = {
    "5' UTR": "#1A1A1A",
    "ORF1a": "#4E79A7",
    "ORF1b": "#A0CBE8",
    "spike": "#E15759",
    "hemagglutinin-esterase": "#F28E2B",
    "envelope": "#EDC948",
    "membrane": "#59A14F",
    "nucleocapsid": "#2F4B7C",
    "accessory": "#B07AA1",
    "3' UTR": "#BDBDBD",
}

# The ORFs on the tracks below: smaller boxes, with their label inside
nested = {
    "markerHeight": 13,
    "arrowheadHeight": 13,
    "fill": "#E8DCE6",
    "stroke": "#B07AA1",
}

nested_label = {"dy": "-1.6em", "fontSize": "8px"}

chart = (
    GC(coronavirus_genomes, cluster="cluster", group="category", height="700px")
    .color(custom_colors=colors)
    # Every gene a box; ORFs that lie inside another gene, e.g. 9b inside N,
    # go on the tracks below. 3c and 3d of SARS-CoV-2 overlap by less than
    # half, so they share a track
    .cluster(prevent_gene_overlap="nested", overlap_min="50%", overlap_spacing=-4)
    .genes(
        marker="box",
        marker_height=18,
        arrowhead_height=18,
        style_by="geneTrack",
        group_style={"2": nested, "3": nested},
    )
    .labels(
        "gene", style_by="geneTrack", group_style={"2": nested_label, "3": nested_label}
    )
    # Homologous genes of neighbouring genomes, coloured by the protein
    # identity, written on each link where it fits
    .links(
        group="homolog",
        measure="identity",
        label=True,
        label_position="link",
        vmin=20,
        curve=True,
        label_style={"fontSize": "9px"},
        color_bar_options={"position": "legend", "legendSide": "right"},
    )
    # Room above the first genome of each genus for its name: 22 pixels more
    # height, taken up by a margin
    .grid(
        margin={"top": 22},
        height=700 / 11 + 22,
        cluster=list(first_of_genus["cluster"]),
    )
    .cluster_label(
        title=list(genomes["cluster"]),
        subtitle=[
            f"<i>{subgenus}</i>, {host}"
            for subgenus, host in zip(genomes["subgenus"], genomes["host"])
        ],
        width="170px",
        font_size="13px",
        subtitle_font={"fontSize": "11px"},
        align="right",
        x=-10,
    )
    .cluster_title(
        title=list(first_of_genus["genus"]),
        cluster=list(first_of_genus["cluster"]),
        align="left",
        height="0px",
        x=-165,
        y=-16,
        title_font={"fontSize": "13px", "fontWeight": "bold"},
    )
    .title(
        "Conserved core, variable accessory genes: coronaviruses of the four genera",
        subtitle="Homologous proteins of close relatives linked by identity; after Fig. 1 of Chazal (2021)",
        height="55px",
        title_font={"fontSize": "16px", "fontWeight": "bold"},
        subtitle_font={"fontSize": "12px", "fontStyle": "italic"},
    )
    .tooltip(formatter="<b>{gene}</b> {product}<br>{virus} {strain}<br>{start} - {end}")
    # The legend names each category with its gene
    .legend(
        position="top",
        align="center",
        order=list(colors),
        legend_text_options={"fontSize": "12px"},
        group_style={
            "5' UTR": {"text": "5' UTR (L)"},
            "spike": {"text": "spike (S)"},
            "hemagglutinin-esterase": {"text": "hemagglutinin-esterase (HE)"},
            "envelope": {"text": "envelope (E)"},
            "membrane": {"text": "membrane (M)"},
            "nucleocapsid": {"text": "nucleocapsid (N)"},
        },
    )
    # The untranslated ends share a pattern, in a shade that shows on each
    .pattern(
        patterns={"5' UTR": "diagonal", "3' UTR": "diagonal"},
        color={"5' UTR": "#8C8C8C", "3' UTR": "#6E6E6E"},
        background=None,
        size=4,
        stroke_width=1,
    )
    .zoom(height=44)
    .theme("publication")
)

chart
