<!-- Made by scripts/export-articles.R from articles/protein-alignment.Rmd. Edit that. -->

# Cluster comparison using protein alignments

This tutorial describes how we can use `geneviewer` to identify and visualize homologous genes across clusters by aligning their proteins. To demonstrate this we use a GenBank file that contains the genes involved in the biosynthesis of erythromycin A from *Saccharopolyspora erythraea* and compare it to several homologous clusters from different species which were identified using [antiSMASH](https://antismash.secondarymetabolites.org/#!/start). For guidance on importing clusters from GenBank files, please refer to [Loading gene clusters from GenBank files](./genbank).

## Materials

The .gbk files and the additional gene info can be downloaded from the [geneviewer-tutorials](https://github.com/nvelden/geneviewer-tutorials/tree/main/Cluster%20comparison%20using%20BlastP) repository. For visualization, the `geneviewer` package is required. Sequence alignment is performed using the `Biostrings` and `pwalign` packages that can be downloaded from Bioconductor.

`protein_blast()` does not run BLAST. It aligns every protein of the query cluster with every protein of the other clusters using a global (Needleman-Wunsch) pairwise alignment and keeps the best hit of each gene. Identity and similarity are counted over the full length of the alignment, gaps included, so they are lower than BLASTP values for proteins that differ in length or share only part of their sequence.

```r
install.packages("geneviewer")
BiocManager::install("Biostrings")
BiocManager::install("pwalign")

library(geneviewer)
library(Biostrings)
library(pwalign)
```

## Loading cluster information

The cluster information needed for the alignments can be loaded directly from the .gbk files by pointing to the folder path that contains the files and running the `protein_blast()` function.

```r
# change the path to the folder where the .gbk files are saved
folder_path <- "~/path/to/folder/"
```

Alternatively, the alignments can be performed using a data.frame that contains the start, end, strand, translation as well as a unique identifier for each gene and cluster as shown below.

|protein_id |translation                                 |cluster    |strand     | start|  end|
|:----------|:-------------------------------------------|:----------|:----------|-----:|----:|
|AAU93784.2 |MIASAPGEEVSLRAVCAAAGVQMPTLYHFFGNKQGLTDAV... |BGC0000054 |complement |   228|  869|
|AAU93785.1 |MSLQYSCIADTCSYSLDIEGVTMSTHTLEGKTVLVAGGAK... |BGC0000054 |forward    |   925| 1746|
|AAU93786.2 |MPSASRRGRRTLHADCDSRAQPENPSACLPWHPPPSSTRR... |BGC0000054 |forward    |  2172| 2729|
|AAU93787.1 |MRGIILAGGTGSRLHPITRGISKQLVPVYDKPMVYYPLST... |BGC0000054 |forward    |  2920| 3813|
|AAU93788.2 |MTIDVPFLDLDAAYVELRPQIDAAVSGVLASGRYLLGAQT... |BGC0000054 |forward    |  3822| 4937|
|AAU93789.1 |MRARQLRVAGGWEFTPTVHHDARGVFASPLQEEAFVAAVG... |BGC0000054 |complement |  4934| 5527|

## Align the proteins

In this tutorial, we will directly input the folder path into the `protein_blast()` function to load our data. We'll select BGC0000055 as our query cluster and align its proteins with those of the other clusters to find their homologs. We use 30 as the minimum identity threshold.

```r
BlastP_results <- geneviewer::protein_blast(
  folder_path,
  query = "BGC0000055",
  id = "protein_id", # Name of column containing gene identifiers. 
  cluster = "cluster", # Name of column containing cluster identifiers. 
  identity = 30
)
```

After the alignment, the dataset will contain four additional columns. These columns are:

-   **BlastP**: The protein id of the best hit in the query cluster (the column keeps this name for compatibility).
-   **identity**: The percentage identity to the best hit.
-   **similarity**: The percentage similarity to the best hit.
-   **score**: Synteny score between clusters based on those used in antiSMASH/MultiGeneBlast.

|protein_id |region                 |cluster    |strand     | start|  end| rowID| identity| similarity|BlastP     | score|
|:----------|:----------------------|:----------|:----------|-----:|----:|-----:|--------:|----------:|:----------|-----:|
|CAM00053.1 |1..381                 |BGC0000055 |forward    |     1|  381|     1|      100|        100|No Hit     |  22.5|
|CAM00054.1 |441..1634              |BGC0000055 |forward    |   441| 1634|     2|      100|        100|CAM00054.1 |  22.5|
|CAM00055.1 |complement(1589..2191) |BGC0000055 |complement |  1589| 2191|     3|      100|        100|CAM00055.1 |  22.5|
|CAM00056.1 |complement(2199..3668) |BGC0000055 |complement |  2199| 3668|     4|      100|        100|CAM00056.1 |  22.5|
|CAM00057.1 |complement(3706..4911) |BGC0000055 |complement |  3706| 4911|     5|      100|        100|CAM00057.1 |  22.5|
|CAM00058.1 |complement(4908..6371) |BGC0000055 |complement |  4908| 6371|     6|      100|        100|CAM00058.1 |  22.5|

We can visualize the results using `geneviewer`. In the graph the clusters are ordered based on the synteny score. The genes are colored by their best hit in the query cluster. Genes that remain uncolored did not have any significant homologs. By hovering over the genes one can see the percentage identity and similarity.

```r
GC_chart(
  data = BlastP_results,
  cluster = "cluster",
  strand = "strand",
  group = "BlastP",
  height = "400px"
) %>%
GC_clusterLabel() %>%
GC_legend(FALSE)
```

@chart article-protein-alignment-1 nocode

## Color by gene function

Rather than assigning colors to genes based on their best hits, we can color them by gene function. To do this we can bind the extra gene information specific to our query cluster from the `BGC0000055_info.csv` file.

```r
# change the path to the folder where BGC0000055_info.csv is saved
BGC0000055_info <- read.csv("~/path/to/folder/BGC0000055_info.csv", fileEncoding = "UTF-8-BOM")
```

|protein_id |Gene    |Position            |Product                                           |Functions                 |
|:----------|:-------|:-------------------|:-------------------------------------------------|:-------------------------|
|CAM00053.1 |        |778214 - 778594 (+) |putative erythromycin esterase                    |Other                     |
|CAM00054.1 |eryK    |778654 - 779847 (+) |cytochrome P450 Erythromycin B/D C-12 hydroxylase |Tailoring (Hydroxylation) |
|CAM00055.1 |eryBVII |779802 - 780404 (-) |dTDP-4-deoxyglucose 3                             |Precursor biosynthesis    |
|CAM00056.1 |eryCV   |780412 - 781881 (-) |EryCV NDP-4,6-dideoxyhexose 3,4-enoyl reductase   |Precursor biosynthesis    |
|CAM00057.1 |eryCIV  |781919 - 783124 (-) |eryCIV NDP-6-deoxyhexose 3,4-dehydratase          |Precursor biosynthesis    |
|CAM00058.1 |eryBVI  |783121 - 784584 (-) |NDP-4-keto-6-deoxy-glucose 2,3-dehydratase        |Precursor biosynthesis    |

By executing a `left_join()` operation with the `BlastP_results` dataset on the `BlastP` field, we can add the extra information to the alignment results.

```r
BlastP_results_functions <- left_join(BlastP_results, BGC0000055_info, by = dplyr::join_by(BlastP == protein_id ) )
```

We can now use the `Function` category to color the genes. We'll also add gene names, links, and identity values to the cluster information.

```r
GC_chart(
  data = BlastP_results_functions,
  cluster = "cluster",
  group = "Functions",
  strand = "strand",
  height = "600px"
) %>%
GC_labels(label = "Gene", cluster = 1) %>% 
GC_links(group = "BlastP",  measure = "identity") %>%  
GC_clusterLabel() %>%
GC_legend(TRUE)
```

@chart article-protein-alignment-2 nocode

Alternatively, the `GC_links()` function allows for highlighting connections between specific genes by utilizing the value1 and value2 parameters. To gain insights into the cluster sizes, we can adjust the axis_type to range. For additional styling and coloring options, refer to the `GC_links()` and `GC_scale()` documentation.

```r
GC_chart(
  data = BlastP_results_functions,
  cluster = "cluster",
  group = "Functions",
  strand = "strand",
  height = "600px"
) %>%
GC_labels(label = "Gene", cluster = 1) %>% 
GC_scale(axis_type = "range") %>%
GC_links(group = "Gene",  
         value1 = c("eryAI", "eryAII", "eryAIII"), 
         value2 = c("eryAI", "eryAII", "eryAIII"), 
         use_group_colors = TRUE
         ) %>%  
GC_clusterLabel() %>%
GC_legend(TRUE)
```

@chart article-protein-alignment-3 nocode
