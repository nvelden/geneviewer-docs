from geneviewer import GC, datasets

pQEB1_plasmids = datasets.load("pQEB1_plasmids")
pQEB1_alignment = datasets.load("pQEB1_alignment")

plasmids = pQEB1_plasmids[["cluster", "host"]].drop_duplicates()

colors = {
    "Carbapenemase (KPC)": "#d62728",
    "Other resistance": "#ff7f0e",
    "Arsenic resistance": "#8c564b",
    "Mobile element": "#9467bd",
    "Conjugation": "#1f77b4",
    "Replication & maintenance": "#2ca02c",
    "Hypothetical": "#d9d9d9",
    "Other": "#9e9e9e",
}

(
    GC(
        pQEB1_plasmids,
        cluster="cluster",
        group="category",
        strand="strand",
        height="760px",
    )
    .links(
        data=pQEB1_alignment,
        measure="none",
        label=False,
        color_bar=False,
        normal_color="#7f9cbf",
        inverted_color="#e6894e",
    )
    .genes(marker_size="small")
    .scale(axis_type="range")
    .cluster_label(
        title=list(plasmids["cluster"]),
        subtitle=list(plasmids["host"]),
        width="175px",
        font_size="13px",
        subtitle_font={"fontSize": "12px", "fontStyle": "italic"},
        align="right",
        x=-10,
    )
    .title(
        "<i>bla</i>KPC-2 plasmid pQEB1 and its rearranged variants",
        subtitle="IncN plasmids aligned with nucmer (all blocks ≥ 99.2% identity); orange links mark inversions",
        height="70px",
        title_font={"fontSize": "20px", "fontWeight": "bold"},
        subtitle_font={"fontSize": "15px", "fontStyle": "italic"},
    )
    .tooltip(formatter="<b>{gene}</b> {product}<br>{start} - {end}")
    .color(custom_colors=colors)
    .legend(
        position="top",
        align="center",
        order=list(colors),
        legend_text_options={"fontSize": "14px"},
    )
    .theme("publication")
)
