# Cluster comparison using protein alignments

This tutorial describes how we can use `geneviewer` to identify and visualize homologous genes across clusters by aligning their proteins. To demonstrate this we use a GenBank file that contains the genes involved in the biosynthesis of erythromycin A from *Saccharopolyspora erythraea* and compare it to several homologous clusters from different species which were identified using [antiSMASH](https://antismash.secondarymetabolites.org/#!/start). For guidance on importing clusters from GenBank files, please refer to [Loading gene clusters from GenBank files](./genbank).

## Materials

The .gbk files and the additional gene info can be downloaded from the [geneviewer-tutorials](https://github.com/nvelden/geneviewer-tutorials/tree/main/Cluster%20comparison%20using%20BlastP) repository. For visualization, the `geneviewer` package is required. Sequence alignment is performed using Biopython, which the `align` extra of the package installs.

`protein_blast()` does not run BLAST. It aligns every protein of the query cluster with every protein of the other clusters using a global (Needleman-Wunsch) pairwise alignment and keeps the best hit of each gene. Identity and similarity are counted over the full length of the alignment, gaps included, so they are lower than BLASTP values for proteins that differ in length or share only part of their sequence.

```sh
pip install "geneviewer-py[align]"
```

```python
import geneviewer as gv
from geneviewer import GC
```

## Loading cluster information

The cluster information needed for the alignments can be loaded directly from the .gbk files by pointing to the folder path that contains the files and running the `protein_blast()` function.

```python norun
# change the path to the folder where the .gbk files are saved
folder_path = "path/to/folder/"
```

Alternatively, the alignments can be performed using a DataFrame that contains the start, end, strand, translation as well as a unique identifier for each gene and cluster as shown below.

```python hide
folder_path = TUTORIALS / "Cluster comparison using BlastP"
gbk = gv.read_gbk(folder_path)
genbank_df = gv.gbk_features_to_df(
    gbk, feature="CDS", keys=["protein_id", "region", "translation"]
).drop(columns="region")
genbank_df = genbank_df[genbank_df["start"].notna() & genbank_df["end"].notna()]
genbank_df["translation"] = genbank_df["translation"].str[:40] + "..."
table(genbank_df)
```

## Align the proteins

In this tutorial, we will directly input the folder path into the `protein_blast()` function to load our data. We'll select BGC0000055 as our query cluster and align its proteins with those of the other clusters to find their homologs. We use 30 as the minimum identity threshold.

```python
BlastP_results = gv.protein_blast(
    folder_path,
    query="BGC0000055",
    id="protein_id",  # Name of column containing gene identifiers.
    cluster="cluster",  # Name of column containing cluster identifiers.
    identity=30,
)
```

After the alignment, the dataset will contain four additional columns. These columns are:

-   **BlastP**: The protein id of the best hit in the query cluster (the column keeps this name for compatibility).
-   **identity**: The percentage identity to the best hit.
-   **similarity**: The percentage similarity to the best hit.
-   **score**: Synteny score between clusters based on those used in antiSMASH/MultiGeneBlast.

```python hide
table(BlastP_results.drop(columns="translation"))
```

We can visualize the results using `geneviewer`. In the graph the clusters are ordered based on the synteny score. The genes are colored by their best hit in the query cluster. Genes that remain uncolored did not have any significant homologs. By hovering over the genes one can see the percentage identity and similarity.

```python
(
    GC(
        BlastP_results,
        cluster="cluster",
        strand="strand",
        group="BlastP",
        height="400px",
    )
    .cluster_label()
    .legend(False)
)
```

## Color by gene function

Rather than assigning colors to genes based on their best hits, we can color them by gene function. To do this we can bind the extra gene information specific to our query cluster from the `BGC0000055_info.csv` file.

```python hide
import pandas as pd

BGC0000055_info = pd.read_csv(folder_path / "BGC0000055_info.csv", encoding="utf-8-sig")
```

```python norun
import pandas as pd

# change the path to the folder where BGC0000055_info.csv is saved
BGC0000055_info = pd.read_csv(
    "path/to/folder/BGC0000055_info.csv", encoding="utf-8-sig"
)
```

```python hide
table(BGC0000055_info)
```

By merging it with the `BlastP_results` dataset on the `BlastP` field, we can add the extra information to the alignment results.

```python
BlastP_results_functions = BlastP_results.merge(
    BGC0000055_info.rename(columns={"protein_id": "BlastP"}), how="left", on="BlastP"
)
```

We can now use the `Function` category to color the genes. We'll also add gene names, links, and identity values to the cluster information.

```python
(
    GC(
        BlastP_results_functions,
        cluster="cluster",
        group="Functions",
        strand="strand",
        height="600px",
    )
    .labels(label="Gene", cluster=1)
    .links(group="BlastP", measure="identity")
    .cluster_label()
    .legend(True)
)
```

Alternatively, the `.links()` method allows for highlighting connections between specific genes by utilizing the value1 and value2 parameters. To gain insights into the cluster sizes, we can adjust the axis_type to range. For additional styling and coloring options, refer to the [`.links()`](../reference/GC-links) and [`.scale()`](../reference/GC-scale) documentation.

```python
(
    GC(
        BlastP_results_functions,
        cluster="cluster",
        group="Functions",
        strand="strand",
        height="600px",
    )
    .labels(label="Gene", cluster=1)
    .scale(axis_type="range")
    .links(
        group="Gene",
        value1=["eryAI", "eryAII", "eryAIII"],
        value2=["eryAI", "eryAII", "eryAIII"],
        use_group_colors=True,
    )
    .cluster_label()
    .legend(True)
)
```
