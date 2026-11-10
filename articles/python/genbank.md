# Loading gene clusters from GenBank files

This tutorial demonstrates creating gene cluster visualizations from GenBank files using `geneviewer`. For guidance on importing clusters from FASTA files see [Loading gene clusters from FASTA files](./fasta). You can obtain GenBank files containing genomic data from a variety of platforms such as [NCBI](https://www.ncbi.nlm.nih.gov/genbank/), [Ensembl](https://www.ensembl.org/), [UCSC](https://genome.ucsc.edu/), [antiSMASH](https://antismash.secondarymetabolites.org/#!/start) and [MIBiG](https://mibig.secondarymetabolites.org/). While `geneviewer` is designed to handle GenBank files from these sources (please report any compatibility issues on [GitHub](https://github.com/nvelden/geneviewer-py/issues)), this tutorial specifically aims to replicate a gene cluster visualization found on the [MIBiG](https://mibig.secondarymetabolites.org/) website.

## Materials

The .gbk files can be downloaded from the [MIBiG](https://mibig.secondarymetabolites.org/) website following the below instructions or directly from the [geneviewer-tutorials](https://github.com/nvelden/geneviewer-tutorials/tree/main/Loading%20GenBank%20files) repository.

## Loading GenBank file

The GenBank files from [MIBiG](https://mibig.secondarymetabolites.org/) include additional details, enabling us to color-code genes by function, which we will use to reproduce the visualizations they show on the website. Begin by downloading a GenBank file from the [MIBiG](https://mibig.secondarymetabolites.org/) website. For the below tutorial we will use the genbank file for gene cluster [BGC0000001](https://mibig.secondarymetabolites.org/repository/BGC0000001/index.html#r1c1). Simply click the "Download GenBank file" link and save the file.

We can load the file using the `read_gbk()` function from `geneviewer`. This will create a dict containing all the sections and features found in the GenBank file.

```python norun
import geneviewer as gv

# change the path to where you have saved the file
file_path = "path/to/file/BGC0000001.gbk"
gbk = gv.read_gbk(file_path)
```

```python hide
import geneviewer as gv

file_path = TUTORIALS / "Loading GenBank files" / "BGC0000001.gbk"
gbk = gv.read_gbk(file_path)
```

We can inspect the .gbk by printing parts of the dict or by simply opening the .gbk file in a text editor. For the visualization we are interested in the start and end position of each gene as well as their identifiers and functions. We can find these under FEATURES > CDS. Let's look at the first CDS to see what information it contains.

```python
cds_1 = gbk["BGC0000001"]["FEATURES"]["CDS"][0]
```

```python hide
import pandas as pd

shown = {key: str(value)[:40] for key, value in cds_1.items()}
table(pd.DataFrame({"key": list(shown), "value": list(shown.values())}), rows=20)
```

We can bind the information of each CDS into a DataFrame using the `gbk_features_to_df()` function. In the below code we define the feature and the keys we are interested in and bind it into a DataFrame. We set `process_region` to `True` which will extract the strand, start and end from the region key.

```python
cds_df = gv.gbk_features_to_df(
    gbk,
    feature="CDS",
    keys=["region", "gene", "protein_id", "gene_kind", "product"],
    process_region=True,
)
```

```python hide
cds_df = cds_df.drop(columns="region")
table(cds_df)
```

## Cluster Visualization

We can see that there are some missing values in the gene_kind column so we will replace those with "other". After we have done that we are ready to make the cluster visualization.

```python
from geneviewer import GC

# replace missing values with "other" for gene_kind
cds_df["gene_kind"] = cds_df["gene_kind"].fillna("other")

# Make the cluster chart
chart = GC(
    cds_df,
    start="start",
    end="end",
    group="gene_kind",
    strand="strand",
    height="180px",
)
chart
```

To make the chart more similar to the one we find on the [MIBiG](https://mibig.secondarymetabolites.org/) website we can add a title, alter the coloring and appearance of the genes and add a scale. In addition, we alter the tooltip to display the gene, product and region on hover.

```python
colors = {
    "biosynthetic": "#810E15",
    "biosynthetic-additional": "#F16D75",
    "transport": "#6495ED",
    "regulatory": "#2E8B57",
    "other": "#808080",
}

(
    chart.genes(
        marker="boxarrow",
        marker_size="small",
        stroke="#6E7079",
        stroke_width=0.5,
    )
    .title(
        "BGC0000001: abyssomicin C biosynthetic gene cluster\n    from <i>Verrucosispora maris</i> AB-18-032",
        align="left",
        title_font={"fontSize": "12px"},
    )
    .scale()
    .color(custom_colors=colors)
    .legend(order=list(colors))
    .tooltip(
        formatter="""
    <b>Gene:</b> {gene}<br>
    <b>Product:</b> {product}<br>
    <b>Region:</b>{start} - {end}
    """
    )
    .theme("classic", text_color="#333333")
)
```

## Loading Multiple GenBank files

The above functions to read and transform .gbk files can also be used to load multiple .gbk files from a folder and show the clusters side by side. To demonstrate this we can go to the cluster page for [BGC0000001](https://mibig.secondarymetabolites.org/repository/BGC0000001/index.html#r1c1) and navigate to the "KnownClusterBlast" page. Click on the homologous clusters and download the .gbk files for [BGC0001694](https://mibig.secondarymetabolites.org/repository/BGC0001694/index.html#r1c1), [BGC0001492](https://mibig.secondarymetabolites.org/repository/BGC0001492/index.html#r1c1), [BGC0001288](https://mibig.secondarymetabolites.org/repository/BGC0001288/index.html#r1c1) and [BGC0000133](https://mibig.secondarymetabolites.org/repository/BGC0000133/index.html#r1c1).

We place all the .gbk files in the same directory and can load them all together as we have done previously.

```python norun
# change the path to the folder containing the .gbk files
folder_path = "path/to/folder/"
gbk_list = gv.read_gbk(folder_path)
```

```python hide
folder_path = TUTORIALS / "Loading GenBank files"
gbk_list = gv.read_gbk(folder_path)
```

We now have a dict of our .gbk files containing the different sections and features. As before we can use the `gbk_features_to_df()` function to make a DataFrame of the features. This time besides the CDS we also make a DataFrame of the source such that we can add the organism name and genomic region as title for each cluster.

```python
cds_clusters_df = gv.gbk_features_to_df(
    gbk_list,
    feature="CDS",
    keys=["region", "gene", "protein_id", "gene_kind", "product"],
    process_region=True,
)
source_clusters_df = gv.gbk_features_to_df(gbk_list, feature="source")
```

```python hide
cds_clusters_df = cds_clusters_df.drop(columns="region")
table(cds_clusters_df)
```

We can now plot the graph but this time we specify the "cluster" column as identifier to distinguish the clusters and add cluster labels and titles.

```python
# replace missing values with "other" for gene_kind
cds_clusters_df["gene_kind"] = cds_clusters_df["gene_kind"].fillna("other")

colors = {
    "biosynthetic": "#810E15",
    "biosynthetic-additional": "#F16D75",
    "transport": "#6495ED",
    "regulatory": "#2E8B57",
    "other": "#808080",
}

# Make the cluster chart
(
    GC(
        cds_clusters_df,
        start="start",
        end="end",
        group="gene_kind",
        strand="strand",
        cluster="cluster",
        height="800px",
    )
    .cluster_title(
        y=5,
        title=[
            f"<i>{organism}</i>: {region}"
            for organism, region in zip(
                source_clusters_df["organism"], source_clusters_df["region"]
            )
        ],
        align="left",
        title_font={"fontSize": 12},
    )
    .cluster_label(list(gbk_list))
    .genes(marker="boxarrow", marker_size="small")
    .scale_bar(title="1kb", scale_bar_unit=1000)
    .color(custom_colors=colors)
    .legend(order=list(colors))
    .tooltip(
        formatter="""
    <b>Gene:</b> {gene}<br>
    <b>ProteinID:</b> {protein_id}<br>
    <b>Product:</b> {product}<br>
    <b>Region:</b>{start} - {end}
    """
    )
    .theme("classic", text_color="#333333")
)
```
