# Genome alignments using MUMmer

This tutorial guides you through the process of performing genome alignments using [MUMmer](https://mummer4.github.io/index.html), an alignment tool widely used for comparing genomic sequences. As an example we will align the plasmids from several species of *B. thuringiensis*. Following the alignment, we'll show you how to visualize the results using **`geneviewer`**.

## Materials

The .gbk files can be downloaded directly from [GenBank](https://www.ncbi.nlm.nih.gov/genbank/) using accession numbers CP000486.1, CP009599.1, CP003188.1 and CP009638.1. Alternatively, you can obtain the GenBank files including all alignment files directly from the [geneviewer-tutorials](https://github.com/nvelden/geneviewer-tutorials/tree/main/MUMmer%20alignments) repository.

## MUMmer alignment

MUMmer needs to be installed on your local machine to execute alignments. For detailed installation instructions, visit the [MUMmer website](https://mummer4.github.io/install/install.html). Once MUMmer is installed, you can perform the alignment using `geneviewer` with the `mummer_alignment()` function. By default it will run the alignment in order of the files in the folder.

**Important** MUMmer cannot use paths with spaces: the names of the files and the folder the alignment runs in (`output_dir`, by default a temporary folder) must be without spaces. The folder of the files may have spaces.

```python norun
import geneviewer as gv

# Change the path to the folder where the .gbk files are saved
folder_path = "path/to/folder/"
```

By default, the `mummer_alignment()` function will perform pairwise alignments starting with the first file in the folder. To adjust the order in which files are aligned, assign a list of file names to the `cluster` argument. By default nucleotide sequences are translated into proteins using "promer" and a "many-to-many" mapping alignment is performed. For the most suitable alignment method for your project, please carefully review the [MUMmer](https://mummer4.github.io/index.html) documentation. To learn how to modify the default settings, see the [`mummer_alignment()`](../reference/mummer_alignment) documentation.

```python norun
alignment = gv.mummer_alignment(
    path=folder_path,
    cluster=None,
    maptype="many-to-many",
    seqtype="protein",
)
```

```python hide
import shutil
import tempfile
from pathlib import Path

import geneviewer as gv

# The files of the tutorials, copied to a temporary folder
folder_path = Path(tempfile.mkdtemp()) / "mummer"
folder_path.mkdir()
for file in sorted((TUTORIALS / "MUMmer alignments").glob("*.gb")):
    shutil.copy(file, folder_path)
alignment = gv.mummer_alignment(
    path=folder_path,
    cluster=None,
    maptype="many-to-many",
    seqtype="protein",
)
```

The alignment generates a DataFrame that details the start and end positions of each aligned region between the reference (cluster1) and query (cluster2), along with identity and similarity scores. This DataFrame can be directly loaded into the `.links()` method.

```python hide
table(alignment)
```

## Synteny gene cluster chart

To map the alignment onto the genome, we must first load the cluster information from the .gbk files. For detailed instructions, please refer to the tutorial [Loading gene clusters from GenBank files](./genbank).

```python
gbk = gv.read_gbk(folder_path)
cds_df = gv.gbk_features_to_df(
    gbk,
    feature="CDS",
    keys=["region", "gene", "protein_id", "note", "product"],
)
```

```python hide
table(cds_df)
```

We can load the cluster data into `GC()` and the alignment data into the `.links()` method. Links run from nearly white at an identity of `vmin` (0 by default) to the full colour at `vmax` (100); setting `vmin` to the lowest identity in the alignment spreads the colours over the data. In addition, we change the axis_type to "range", make the genes a little smaller, add cluster labels and use the `"publication"` theme. For more customization options see [Get started](/getting-started?lang=py).

**Important**: The gene cluster data like the alignment data is loaded in the order of the files in the folder. If a custom order was used for the MUMmer alignment make sure to sort the "cluster" column in the cluster data in the same way.

```python
import math

from geneviewer import GC

(
    GC(cds_df, strand="strand", cluster="cluster")
    .links(
        data=alignment,
        measure="identity",
        vmin=math.floor(alignment["identity"].min()),
    )
    .scale(axis_type="range")
    .cluster(separate_strands=True)
    .genes(marker_size="small")
    .cluster_label(
        title=["pALH1", "pBFQ", "F837_55", "pBFI_4"],
        width="75px",
        font_size="12px",
    )
    .tooltip(formatter="<b>{protein_id}</b><br>{start} - {end}")
    .legend(False)
    .theme("publication")
)
```
