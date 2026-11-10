# Loading gene clusters from FASTA files

This tutorial demonstrates creating gene cluster visualizations from FASTA files using `geneviewer`. For guidance on importing clusters from GenBank files see [Loading gene clusters from GenBank files](./genbank). `geneviewer` parses FASTA headers to extract key-value pairs, denoted by =.  For instance, in the below FASTA header it identifies 'protein' as 'putative phosphoenolpyruvate synthase' and similarly processes other pairs. The 'location' tag is crucial because it allows the extraction of 'start', 'end', and 'strand' information for each gene.

```text
>lcl|HQ3864.1_prot_ADX475.1_1 protein=putative phosphoenolpyruvate synthase protein_id=ADX66475.1 location=complement(<1..2247) gbkey=CDS
MRATGLVRGRAAKRFGRAGGAGDAIGQCRATGHDCLGGSAMIEQYVWDLHEVDETQVAVVGGKGAHLGGL
SRIEGIRVPAGFCVTTDAFRRIMAEAPSIDDGLDQLSRLNPDDREAIRTLSAQIRRTIEGIAIPGDLAAA
ITRALARLGEHAACAVRSSATAEDLPTASFAGQQDTYLNVVGPTAILQHVSRCWASLFTERAVTYRQRNG
```

## Materials

The FASTA files used for the tutorial were originally downloaded from the [NCBI](https://www.ncbi.nlm.nih.gov/nuccore) website but can be downloaded directly from the [geneviewer-tutorials](https://github.com/nvelden/geneviewer-tutorials/tree/main/Loading%20FASTA%20files) repository.

## Loading FASTA files

The example FASTA files used for this tutorial are each from a different organism and holds the genes of a cluster that produces a polyene antifungal agent. Download the files and place them under the same folder. We can read the files using the `read_fasta()` function from `geneviewer`. The function will parse all the FASTA headers and create a DataFrame from the extracted information. We have set sequence to `False` since we do not need the sequences to create the cluster visualization.

```python norun
import geneviewer as gv

# change the path to the folder where you have saved the file
file_path = "path/to/folder/"
fasta_df = gv.read_fasta(file_path, sequence=False)
```

```python hide
import geneviewer as gv

file_path = TUTORIALS / "Loading FASTA files"
fasta_df = gv.read_fasta(file_path, sequence=False)
```

The DataFrame holds the protein IDs, start, end and strand information for each gene. In addition there is the cluster column that tells us from which file each gene is coming.

```python hide
table(fasta_df)
```

## Cluster Visualization

Using the DataFrame we created from the FASTA files we can now easily make the cluster visualization.

```python
from geneviewer import GC

# Make the cluster chart
chart = GC(
    fasta_df,
    start="start",
    end="end",
    strand="strand",
    cluster="cluster",
    height="400px",
).cluster_label(list(fasta_df["cluster"].unique()))
chart
```

## UniProt keywords

We can get additional information for each gene from [UniProt](https://www.uniprot.org/). Its [ID mapping](https://www.uniprot.org/id-mapping) page maps identifiers from one database to another: paste the protein IDs (`fasta_df["protein_id"]`), map from "EMBL/GenBank/DDBJ CDS" to "UniProtKB", add the "Keywords" column to the results and download them as a TSV file. For this tutorial we want the keywords associated with each gene such that we can use them to group the genes based on their function.

```python norun
import pandas as pd

# change the path to where you have saved the file
keywords = pd.read_csv("path/to/file/keywords.tsv", sep="\t")
```

```python hide
import pandas as pd

# The output on this page comes from a saved copy of UniProt's answer, so it
# does not depend on the UniProt servers.
keywords = pd.read_csv("articles/data/fasta-keywords.tsv", sep="\t")
```

This gives a DataFrame with our original identifiers, UniProt IDs and the keywords associated with each gene. UniProt only returns the genes that have an active UniProtKB entry, here 113 of the 132. The 19 genes of cluster BGC0001709 have none, so they end up in the Other group below.

```python hide
table(keywords)
```

We now do a bit of data wrangling with pandas performing the following steps:

-   We split the keywords for each gene on ";"
-   Count the occurrence of each keyword
-   For each gene keep only the highest occurring keyword
-   Replace any keyword that has less then 10 occurrences to "Other"
-   Bind the keywords to our fasta_df by protein ID
-   Replace any genes without keyword to Other
-   Select only the columns we need for our visualization

```python
# Separate the Keywords into different rows
keywords_count = keywords.assign(Keywords=keywords["Keywords"].str.split(";"))
keywords_count = keywords_count.explode("Keywords", ignore_index=True)
# Replace missing values with 'Other'
keywords_count["Keywords"] = keywords_count["Keywords"].fillna("Other")
# Add a column n that counts each Keyword
keywords_count["n"] = keywords_count.groupby("Keywords")["Keywords"].transform("size")

# Keep the top ranking keyword for each protein ID
top = keywords_count.groupby("From")["n"].idxmax()
keywords_count = keywords_count.loc[top]

# Replace any keyword that has a count less then 10 with "Other"
keywords_count.loc[keywords_count["n"] < 10, "Keywords"] = "Other"

# Bind Keywords back to fasta_df
fasta_df_with_keywords = fasta_df.merge(
    keywords_count, how="left", left_on="protein_id", right_on="From"
)
fasta_df_with_keywords["Keywords"] = fasta_df_with_keywords["Keywords"].fillna("Other")
fasta_df_with_keywords = fasta_df_with_keywords[
    ["cluster", "start", "end", "strand", "protein_id", "protein", "Keywords", "n"]
]
```

```python hide
table(fasta_df_with_keywords)
```

We can now make our visual again but use the keywords to group the genes. We alter the order of the legend such that it is in alphabetical order and the Other group is placed last and finally we customize the tooltip to also show the protein Id on hover.

```python
key_legend = sorted(set(fasta_df_with_keywords["Keywords"]) - {"Other"}) + ["Other"]

# Make the cluster chart
chart = (
    GC(
        fasta_df_with_keywords,
        start="start",
        end="end",
        strand="strand",
        group="Keywords",
        cluster="cluster",
        height="400px",
    )
    .cluster_label(list(fasta_df["cluster"].unique()))
    .legend(order=key_legend)
    .tooltip(
        formatter="""
    <b>ProteinID:</b> {protein_id}<br>
    <b>Region:</b> {start} - {end}
    """
    )
)
chart
```

For further customization options like setting a title, altering the colors adding gene links and much more see [Get started](/getting-started?lang=py) and [Examples](/examples?lang=py).
