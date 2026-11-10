---
prev:
  text: Reading files
  link: /python/reading-files
next:
  text: Reference
  link: /python/reference/
---

# Alignment

Two functions compare clusters, for the colours and links of a chart: [`protein_blast()`](./reference/protein_blast) aligns the proteins of the clusters, and [`mummer_alignment()`](./reference/mummer_alignment) aligns their DNA with MUMmer.

## Protein alignment

`protein_blast()` aligns every protein of a query cluster with every protein of the other clusters, and gives each gene its best hit in the query cluster. It needs the `align` extra, which installs Biopython:

```sh
pip install "geneviewer-py[align]"
```

It takes a table of genes with their protein sequence in a column `translation` (or `sequence`), or the path of a folder of GenBank files, with a cluster per file. This uses the sequences of the `erythromycin_BlastP` dataset: five erythromycin gene clusters.

```python
import geneviewer as gv
from geneviewer import GC, datasets

genes = datasets.load("erythromycin_BlastP")[
    ["protein_id", "region", "translation", "cluster", "strand", "start", "end"]
]
hits = gv.protein_blast(genes, query="BGC0000055", identity=30)
hits = hits.drop(columns="translation")
```

The result is the table with four more columns: `BlastP`, the id of the query protein that is the best hit of the gene (`"No Hit"` without one), `identity` and `similarity` in percent, and `score`, by which the clusters are ordered, the most similar to the query first. Grouping and linking by `BlastP` colours each gene as its hit and joins them:

@chart python-protein-alignment

Despite its name, the function does not run BLAST. It makes a global (Needleman-Wunsch) alignment of each pair, and counts identity and similarity over the full length of the alignment, gaps included. Proteins that differ much in length, or share one domain only, get lower values than BLASTP gives them.

The R package aligns with another library, which can pick another of several equally good alignments. For some pairs the identity and similarity then differ a little from R's; see [Differences from R](./differences).

## MUMmer alignment

`mummer_alignment()` aligns each cluster with the next one, with `nucmer` (DNA) or `promer` (translated DNA) of [MUMmer](https://mummer4.github.io/), which must be installed and in the PATH. Each cluster is a FASTA or GenBank file, named after the cluster, in one folder:

```python
import geneviewer as gv

alignment = gv.mummer_alignment(
    "plasmids",
    cluster=["pQEB1_inv3_Tn5403", "pQEB1", "pQEB1_del1"],
    seqtype="nucleotide",
)
```

The result has a row per aligned block: its start and end in both clusters, its length and identity, and the names of the two clusters. `.links(data=...)` draws a table of that form. The `pQEB1_alignment` dataset is such a table, for the plasmids of the `pQEB1_plasmids` dataset; inverted blocks get their own colour:

@chart python-alignment-links

A pair of clusters without alignments gives no rows. MUMmer 3's `promer` can give slightly different alignments from one run to the next on the same files.
