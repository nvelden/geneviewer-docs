<!-- Made by scripts/export-python-articles.py from articles/python/gff.md. Edit that. -->

# Loading gene clusters from generic feature format (.gff) files

This tutorial demonstrates creating gene cluster visualizations from Generic Feature Format (GFF) files using `geneviewer`. You can obtain .gff files from a variety of platforms such as [NCBI](https://www.ncbi.nlm.nih.gov/genbank/), [Ensembl](https://www.ensembl.org/) or [UCSC](https://genome.ucsc.edu/). This tutorial demonstrates how to load and visualize several viral genomes in .gff format using geneviewer.

## Materials

The .gff files were retrieved from the [Ensembl](https://www.ensembl.org/) website by searching with their respective GenBank identifiers and downloading the records in GFF3 format. Alternatively, the files can also be directly accessed from the [geneviewer-tutorials](https://github.com/nvelden/geneviewer-tutorials/tree/main/Loading%20GFF%20files) repository.

## Loading GFF files

We can load the .gff files using the `read_gff()` function from the geneviewer package. To do this, we can either load each file individually by specifying its file path, or load all files at once by specifying the directory that contains all the .gff files.

In the example below, we load all .gff files from a specified directory using the `fields` parameter to select specific fields for loading. If no fields are specified, all fields will be loaded by default. We filter the data to select entries where the 'type' column contains 'CDS'. In addition we add an extra column which maps each GenBank ID in the `filename` column to its corresponding viral name.

```python
import geneviewer as gv

# change the path to where you have saved the
# file or the directory containing all .gff files
folder_path = "path/to/folder/"
gff = gv.read_gff(
    folder_path, fields=["source", "type", "start", "end", "strand", "Name"]
)
gff = gff[gff["type"] == "CDS"]

# Add viral names
virus_names = {
    "GU071086": "Marseillevirus",
    "HQ113105.1": "Lausannevirus",
    "KF261120": "Cannesvirus",
    "KF483846": "Tunisvirus",
}
gff["Virus"] = gff["filename"].map(virus_names)
```

| source | type | start | end | strand | Name | filename | Virus |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Genbank | CDS | 293 | 1039 | - | ADB03794.1 | GU071086 | Marseillevirus |
| Genbank | CDS | 1146 | 1802 | - | ADB03795.1 | GU071086 | Marseillevirus |
| Genbank | CDS | 1950 | 2714 | - | ADB03796.1 | GU071086 | Marseillevirus |
| Genbank | CDS | 2737 | 3210 | - | ADB03797.1 | GU071086 | Marseillevirus |
| Genbank | CDS | 3242 | 3520 | - | ADB03798.1 | GU071086 | Marseillevirus |
| Genbank | CDS | 3566 | 4048 | - | ADB03799.1 | GU071086 | Marseillevirus |

We can now visualize the genomic data using `geneviewer`. The chart displays the start and end positions of genes for each viral genome oriented according to strand location. A custom title is added to the chart, and the gene clusters are labeled with their viral names. The axis is set to `range` to facilitate size comparisons among the genomes. Additionally, the visual representation of the genes is simplified by removing outlines (strokes) and using smaller markers. As a final touch we change the tooltip to only display the gene Name.

```python
from geneviewer import GC

(
    GC(
        gff,
        start="start",
        end="end",
        strand="strand",
        cluster="Virus",
        height="400px",
    )
    .title("<i>Marseilleviridae</i> viral genomes")
    .cluster_label()
    .scale(axis_type="range")
    .genes(group="filename", stroke="none", marker_size="small")
    .tooltip(formatter="<b>Gene:</b> {Name}")
)
```

@chart article-gff-1 nocode
