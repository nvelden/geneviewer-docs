<!-- Made by scripts/export-articles.R from articles/mummer.Rmd. Edit that. -->

# Genome alignment using MUMmer

This tutorial guides you through the process of performing genome alignments using [MUMmer](https://mummer4.github.io/index.html), an alignment tool widely used for comparing genomic sequences. As an example we will align the plasmids from several species of *B. thuringiensis*. Following the alignment, we'll show you how to visualize the results using **`geneviewer`**.

## Materials

The .gbk files can be downloaded directly from [GenBank](https://www.ncbi.nlm.nih.gov/genbank/) using accession numbers CP000486.1, CP009599.1, CP003188.1 and CP009638.1. Alternatively, you can obtain the GenBank files including all alignment files directly from the [geneviewer-tutorials](https://github.com/nvelden/geneviewer-tutorials/tree/main/MUMmer%20alignments) repository.

## MUMmer alignment

MUMmer needs to be installed on your local machine to execute alignments. For detailed installation instructions, visit the [MUMmer website](https://mummer4.github.io/install/install.html). Once MUMmer is installed, you can perform the alignment using `geneviewer` with the `mummer_alignment()` function. By default it will run the alignment in order of the files in the folder.

**Important** MUMmer requires file paths without spaces. From geneviewer 0.2.1, the folder of the files may have spaces; the names of the files and the folder the alignment runs in (`output_dir`, by default a temporary folder) must still be without spaces.

```r
library(geneviewer)
# Change the path to the folder where the .gbk files are saved
folder_path <- "~/path/to/folder/"
```

By default, the `mummer_alignment()` function will perform pairwise alignments starting with the first file in the folder. To adjust the order in which files are aligned, assign a vector of file names to the `cluster` variable. By default nucleotide sequences are translated into proteins using "promer" and a "many-to-many" mapping alignment is performed. For the most suitable alignment method for your project, please carefully review the [MUMmer](https://mummer4.github.io/index.html) documentation. To learn how to modify the default settings, consult the documentation by running `?mummer_alignment()`.

```r
alignment <- 
  mummer_alignment(
    path = folder_path,
    cluster = NULL,
    maptype = "many-to-many",
    seqtype = "protein"
  )
```

The alignment generates a data frame that details the start and end positions of each aligned region between the reference (cluster1) and query (cluster2), along with identity and similarity scores. This data frame can be directly loaded into the `GC_links()` function.

|               | start1|  end1| start2|  end2| length1| length2| identity| similarity| stop| frame1| frame2|tag1       |tag2       |cluster1     |cluster2     |
|:--------------|------:|-----:|------:|-----:|-------:|-------:|--------:|----------:|----:|------:|------:|:----------|:----------|:------------|:------------|
|1_CP000486.1.1 |      3| 51542|  51540|     1|   51540|   51540|   100.00|     100.00| 5.53|      3|     -2|CP000486.1 |CP009599.1 |1_CP000486.1 |2_CP009599.1 |
|1_CP000486.1.2 |  55939| 51545|  51543| 55937|    4395|    4395|   100.00|     100.00| 6.01|     -1|      3|CP000486.1 |CP009599.1 |1_CP000486.1 |2_CP009599.1 |
|2_CP009599.1.1 |   1013|  3202|  47346| 45157|    2190|    2190|    92.33|      94.38| 6.37|      2|     -3|CP009599.1 |CP003188.1 |2_CP009599.1 |3_CP003188.1 |
|2_CP009599.1.2 |   3354|  4118|  44995| 44267|     765|     729|    57.98|      74.32| 2.33|      3|     -2|CP009599.1 |CP003188.1 |2_CP009599.1 |3_CP003188.1 |
|2_CP009599.1.3 |   4113|  9041|  44270| 39342|    4929|    4929|    94.83|      96.41| 4.66|      3|     -1|CP009599.1 |CP003188.1 |2_CP009599.1 |3_CP003188.1 |
|2_CP009599.1.4 |   9772| 10803|  38441| 37422|    1032|    1020|    61.78|      72.70| 0.29|      1|     -1|CP009599.1 |CP003188.1 |2_CP009599.1 |3_CP003188.1 |

## Synteny gene cluster chart

To map the alignment onto the genome, we must first load the cluster information from the .gbk files. For detailed instructions, please refer to the tutorial [Loading gene clusters from GenBank files](./genbank).

```r
folder_path <- "~/path/to/folder/"
gbk <- read_gbk(folder_path)
cds_df <- gbk_features_to_df(
  gbk, 
  feature = "CDS",
  keys = c("region", "gene", "protein_id", "note", "product")
  )
```

|region                 |gene |protein_id |product                           |note                                              |cluster      |strand     | start|  end|
|:----------------------|:----|:----------|:---------------------------------|:-------------------------------------------------|:------------|:----------|-----:|----:|
|complement(665..1603)  |terS |ABK88159.1 |phage terminase small subunit     |NA                                                |1_CP000486.1 |complement |   665| 1603|
|complement(2151..2975) |uvrC |ABK88160.1 |possible excinuclease ABC subunit |NA                                                |1_CP000486.1 |complement |  2151| 2975|
|complement(2988..3599) |res  |ABK88161.1 |resolvase                         |NA                                                |1_CP000486.1 |complement |  2988| 3599|
|complement(4075..4305) |NA   |ABK88162.1 |conserved hypothetical protein    |possible phage-related protein, N-terminal region |1_CP000486.1 |complement |  4075| 4305|
|complement(4394..4720) |NA   |ABK88163.1 |hypothetical protein              |NA                                                |1_CP000486.1 |complement |  4394| 4720|
|complement(5796..6185) |NA   |ABK88164.1 |phage-related protein             |NA                                                |1_CP000486.1 |complement |  5796| 6185|

We can load the cluster data into the `GC_chart()` and the alignment data into the `GC_links()` function. Links run from nearly white at an identity of `vmin` (0 by default) to the full colour at `vmax` (100); setting `vmin` to the lowest identity in the alignment spreads the colours over the data. In addition, we change the axis_type to "range", make the genes a little smaller, add cluster labels and use the `"publication"` theme. For more customization options see [Get started](/getting-started?lang=r).

**Important**: The gene cluster data like the alignment data is loaded in the order of the files in the folder. If a custom order was used for the MUMmer alignment make sure to sort the "cluster" column in the cluster data in the same way.

```r
GC_chart(cds_df, strand = "strand", cluster = "cluster") %>%
  GC_links(data = alignment, measure = "identity", vmin = floor(min(alignment$identity))) %>%
  GC_scale(axis_type = "range") %>%
  GC_cluster(separate_strands = TRUE) %>%
  GC_genes(marker_size = "small") %>%
  GC_clusterLabel(
    title = c("pALH1", "pBFQ", "F837_55", "pBFI_4"),
    width = "75px",
    fontSize = "12px"
  ) %>%
  GC_tooltip(formatter = "<b>{protein_id}</b><br>{start} - {end}") %>%
  GC_legend(FALSE) %>%
  GC_theme("publication")
```

@chart article-mummer-1 nocode
