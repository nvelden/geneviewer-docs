<!-- Made by scripts/export-python-articles.py from articles/python/fasta.md. Edit that. -->

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

```python
import geneviewer as gv

# change the path to the folder where you have saved the file
file_path = "path/to/folder/"
fasta_df = gv.read_fasta(file_path, sequence=False)
```

The DataFrame holds the protein IDs, start, end and strand information for each gene. In addition there is the cluster column that tells us from which file each gene is coming.

| protein | protein_id | location | gbkey | gene | start | end | strand | cluster | locus_tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| putative phosphoenolpyruvate synthase | ADX66475.1 | complement(&lt;1..2247) | CDS | NA | 1 | 2247 | complement | BGC0000108 | NA |
| putative RNA polymerase sigma factor | ADX66476.1 | complement(3301..3870) | CDS | sigD | 3301 | 3870 | complement | BGC0000108 | NA |
| conserved hypothetical protein | ADX66477.1 | complement(4356..5282) | CDS | calU-c | 4356 | 5282 | complement | BGC0000108 | NA |
| ScnRII | ADX66474.1 | complement(5576..6154) | CDS | scnRII | 5576 | 6154 | complement | BGC0000108 | NA |
| ScnRI | ADX66458.1 | 6555..10085 | CDS | scnRI | 6555 | 10085 | forward | BGC0000108 | NA |
| putative glucosyl transferase | ADD85130.2 | 10250..11626 | CDS | scnK | 10250 | 11626 | forward | BGC0000108 | NA |

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

@chart article-fasta-1 nocode

## UniProt keywords

We can get additional information for each gene from [UniProt](https://www.uniprot.org/). Its [ID mapping](https://www.uniprot.org/id-mapping) page maps identifiers from one database to another: paste the protein IDs (`fasta_df["protein_id"]`), map from "EMBL/GenBank/DDBJ CDS" to "UniProtKB", add the "Keywords" column to the results and download them as a TSV file. For this tutorial we want the keywords associated with each gene such that we can use them to group the genes based on their function.

```python
import pandas as pd

# change the path to where you have saved the file
keywords = pd.read_csv("path/to/file/keywords.tsv", sep="\t")
```

This gives a DataFrame with our original identifiers, UniProt IDs and the keywords associated with each gene. UniProt only returns the genes that have an active UniProtKB entry, here 113 of the 132. The 19 genes of cluster BGC0001709 have none, so they end up in the Other group below.

| From | Entry | Keywords |
| --- | --- | --- |
| AAF71762.1 | Q9L4X7 | Magnesium;Metal-binding;Transferase |
| AAF71763.1 | Q9L4X6 | ATP-binding;Cell membrane;Membrane;Nucleotide-binding;Transmembrane;Transmembrane helix;Transport |
| AAF71764.1 | Q9L4X5 | ATP-binding;Cell membrane;Membrane;Nucleotide-binding;Transmembrane;Transmembrane helix;Transport |
| AAF71765.1 | Q9L4X4 | Lyase;NADP |
| AAF71766.1 | Q9L4X3 | Acyltransferase;Antibiotic biosynthesis;Multifunctional enzyme;Phosphopantetheine;Phosphoprotein;Transferase |
| AAF71767.1 | Q9L4X2 | Acyltransferase;Antibiotic biosynthesis;Multifunctional enzyme;Phosphopantetheine;Phosphoprotein;Transferase |

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

| cluster | start | end | strand | protein_id | protein | Keywords | n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BGC0000108 | 1 | 2247 | complement | ADX66475.1 | putative phosphoenolpyruvate synthase | Nucleotide-binding | 19 |
| BGC0000108 | 3301 | 3870 | complement | ADX66476.1 | putative RNA polymerase sigma factor | DNA-binding | 21 |
| BGC0000108 | 4356 | 5282 | complement | ADX66477.1 | conserved hypothetical protein | Other | 4 |
| BGC0000108 | 5576 | 6154 | complement | ADX66474.1 | ScnRII | DNA-binding | 21 |
| BGC0000108 | 6555 | 10085 | forward | ADX66458.1 | ScnRI | DNA-binding | 21 |
| BGC0000108 | 10250 | 11626 | forward | ADD85130.2 | putative glucosyl transferase | Transferase | 40 |

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

@chart article-fasta-2 nocode

For further customization options like setting a title, altering the colors adding gene links and much more see [Get started](/getting-started?lang=py) and [Examples](/examples?lang=py).
