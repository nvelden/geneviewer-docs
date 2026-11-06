<!-- Made by scripts/export-articles.R from articles/fasta.Rmd. Edit that. -->

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

The example FASTA files used for this tutorial are each from a different organism and holds the genes of a cluster that produces a polyene antifungal agent. Download the files and place them under the same folder. We can read the files into R using the `read_fasta` function from `geneviewer`. The function will parse all the FASTA headers and create a data.frame from the extracted information. We have set sequence to `FALSE` since we do not need the sequences to create the cluster visualization.

```r
library(geneviewer)

# change the path to the folder where you have saved the file
file_path <- "~/path/to/folder/"
fasta_df <- read_fasta(file_path, sequence = FALSE)
View(fasta_df) # Inspect the data.frame in Rstudio
```

The data.frame holds the protein IDs, start, end and strand information for each gene. In addition there is the cluster column that tells us from which file each gene is coming.

|protein                               |protein_id |location               |gbkey |gene   | start|   end|strand     |cluster    |locus_tag |
|:-------------------------------------|:----------|:----------------------|:-----|:------|-----:|-----:|:----------|:----------|:---------|
|putative phosphoenolpyruvate synthase |ADX66475.1 |complement(&lt;1..2247)   |CDS   |NA     |     1|  2247|complement |BGC0000108 |NA        |
|putative RNA polymerase sigma factor  |ADX66476.1 |complement(3301..3870) |CDS   |sigD   |  3301|  3870|complement |BGC0000108 |NA        |
|conserved hypothetical protein        |ADX66477.1 |complement(4356..5282) |CDS   |calU-c |  4356|  5282|complement |BGC0000108 |NA        |
|ScnRII                                |ADX66474.1 |complement(5576..6154) |CDS   |scnRII |  5576|  6154|complement |BGC0000108 |NA        |
|ScnRI                                 |ADX66458.1 |6555..10085            |CDS   |scnRI  |  6555| 10085|forward    |BGC0000108 |NA        |
|putative glucosyl transferase         |ADD85130.2 |10250..11626           |CDS   |scnK   | 10250| 11626|forward    |BGC0000108 |NA        |

## Cluster Visualization

Using the data.frame we created from the FASTA files we can now easily make the cluster visualization.

```r
# Make the cluster chart
chart <- GC_chart(
  fasta_df,
  start = "start",
  end = "end",
  strand = "strand",
  cluster = "cluster",
  height = "400px"
) %>% 
  GC_clusterLabel(unique(fasta_df$cluster))
chart
```

@chart article-fasta-1 nocode

## UniProt keywords

We can get additional information for each gene using the `UniProt.ws` package. We make the connection to the database using the `UniProt.ws` function. Using `keytypes(up)` we can see all the keys we can use to query the database and with `columns(up)` we can see all the different fields we can get in return. Our gene IDs are EMBL-GenBank-DDBJ_CDS identifiers. For this tutorial we want to return the keywords associated with each gene such that we can use them to group the genes based on their function.

On a Mac, if `UniProt.ws()` does not finish, update the `curl` package with `install.packages("curl")` and restart R. Versions before 6.2.0 cannot read UniProt's answers there.

```r
# install.packages("BiocManager")
# BiocManager::install("UniProt.ws")
# install.packages("tidyr")
library(UniProt.ws)

up <- UniProt.ws::UniProt.ws()

keytypes(up)
columns(up)

keywords <- UniProt.ws::select(
  up, 
  column = c("keyword"), 
  keys = fasta_df$protein_id, 
  keytype = "EMBL-GenBank-DDBJ_CDS"
  )
```

This will return a data.frame with our original identifiers, UniProt IDs and the keywords associated with each gene. UniProt only returns the genes that have an active UniProtKB entry, here 113 of the 132. The 19 genes of cluster BGC0001709 have none, so they end up in the Other group below.

|From       |Entry  |Keywords                                                                                                     |
|:----------|:------|:------------------------------------------------------------------------------------------------------------|
|AAF71762.1 |Q9L4X7 |Magnesium;Metal-binding;Transferase                                                                          |
|AAF71763.1 |Q9L4X6 |ATP-binding;Cell membrane;Membrane;Nucleotide-binding;Transmembrane;Transmembrane helix;Transport            |
|AAF71764.1 |Q9L4X5 |ATP-binding;Cell membrane;Membrane;Nucleotide-binding;Transmembrane;Transmembrane helix;Transport            |
|AAF71765.1 |Q9L4X4 |Lyase;NADP                                                                                                   |
|AAF71766.1 |Q9L4X3 |Acyltransferase;Antibiotic biosynthesis;Multifunctional enzyme;Phosphopantetheine;Phosphoprotein;Transferase |
|AAF71767.1 |Q9L4X2 |Acyltransferase;Antibiotic biosynthesis;Multifunctional enzyme;Phosphopantetheine;Phosphoprotein;Transferase |

We now do a bit of data wrangling with the help of the `dplyr` package performing the following steps:

-   We split the keywords for each gene on ";"
-   Count the occurrence of each keyword
-   For each gene keep only the highest occurring keyword
-   Replace any keyword that has less then 10 occurrences to "Other"
-   Bind the keywords to our fasta_df by protein ID
-   Replace any genes without keyword to Other
-   Select only the columns we need for our visualization

```r
library(dplyr)

keywords_count <- keywords %>%
  # Separate the Keywords into different rows
  tidyr::separate_rows(Keywords, sep = ";") %>%
  # Replace NA values with 'Other'
  mutate(Keywords = replace(Keywords, is.na(Keywords), "Other")) %>%
  # Add a Count column that counts each Keyword
  add_count(Keywords)

# Keep top ranking keywords for each protein ID
keywords_count <- keywords_count %>%
  group_by(From) %>%
  filter(rank(-n, ties.method = "first") == 1) %>%
  ungroup()

# Replace any keyword that has a count less then 10 with "Other"
keywords_count <- keywords_count %>%
  mutate(Keywords = ifelse(n < 10, "Other", Keywords))

# Bind Keywords back to fasta_df
fasta_df_with_keywords <- 
  left_join(fasta_df, keywords_count, by = c("protein_id" = "From")) %>% 
  mutate(Keywords = replace(Keywords, is.na(Keywords), "Other")) %>%
  select(cluster, start, end, strand, protein_id, protein, Keywords, n)
```

|cluster    | start|   end|strand     |protein_id |protein                               |Keywords           |  n|
|:----------|-----:|-----:|:----------|:----------|:-------------------------------------|:------------------|--:|
|BGC0000108 |     1|  2247|complement |ADX66475.1 |putative phosphoenolpyruvate synthase |Nucleotide-binding | 19|
|BGC0000108 |  3301|  3870|complement |ADX66476.1 |putative RNA polymerase sigma factor  |DNA-binding        | 21|
|BGC0000108 |  4356|  5282|complement |ADX66477.1 |conserved hypothetical protein        |Other              |  4|
|BGC0000108 |  5576|  6154|complement |ADX66474.1 |ScnRII                                |DNA-binding        | 21|
|BGC0000108 |  6555| 10085|forward    |ADX66458.1 |ScnRI                                 |DNA-binding        | 21|
|BGC0000108 | 10250| 11626|forward    |ADD85130.2 |putative glucosyl transferase         |Transferase        | 40|

We can now make our visual again but use the keywords to group the genes. We alter the order of the legend such that it is in alphabetical order and the Other group is placed last and finally we customize the tooltip to also show the protein Id on hover.

```r
key_legend <- c(setdiff(sort(unique(fasta_df_with_keywords$Keywords)), "Other"), "Other")

# Make the cluster chart
chart <- GC_chart(
  fasta_df_with_keywords,
  start = "start",
  end = "end",
  strand = "strand",
  group = "Keywords",
  cluster = "cluster",
  height = "400px"
) %>% 
  GC_clusterLabel(unique(fasta_df$cluster)) %>%
  GC_legend(order = key_legend) %>%
  GC_tooltip(
    formatter = "
    <b>ProteinID:</b> {protein_id}<br>
    <b>Region:</b> {start} - {end}
    "
  )
chart
```

@chart article-fasta-2 nocode

For further customization options like setting a title, altering the colors adding gene links and much more see [Get started](/getting-started?lang=r) and [Examples](/examples?lang=r).
