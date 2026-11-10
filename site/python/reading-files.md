---
prev:
  text: Shiny for Python
  link: /python/shiny
next:
  text: Alignment
  link: /python/alignment
---

# Reading files

The readers turn GenBank, GFF, FASTA and BED files into pandas DataFrames, with the columns the R package's readers give. Each takes the path of a file, or of a folder to read every file in it.

| Function | Reads |
| --- | --- |
| [`read_gbk()`](./reference/read_gbk) | GenBank files (`.gbk`, `.gb`), as records with their features |
| [`gbk_features_to_df()`](./reference/gbk_features_to_df) | A table of one kind of feature from those records |
| [`read_gff()`](./reference/read_gff) | GFF3 and GTF files |
| [`read_fasta()`](./reference/read_fasta) | FASTA files, with the keys of their headers as columns |
| [`read_bed()`](./reference/read_bed) | BED files |
| [`genbank_to_fasta()`](./reference/genbank_to_fasta) | Writes the sequence of a GenBank file as FASTA |

## GenBank files

`GC()` takes the path of a GenBank file, or of a folder of them, and draws the coding sequences, with a cluster per file:

@chart python-genbank

For other features or more of their qualifiers, read the file and pick them. `read_gbk()` gives the records of the file, and `gbk_features_to_df()` a table of one kind of feature, with a column for each key. The key `region` gives the columns `start`, `end` and `strand`:

```python
import geneviewer as gv

records = gv.read_gbk("BGC0000001.gbk")
cds = gv.gbk_features_to_df(
    records, feature="CDS", keys=["region", "gene", "product", "gene_kind"]
)
```

@chart python-genbank-features

## GFF, FASTA and BED files

```python
import geneviewer as gv

genes = gv.read_gff("annotation.gff3")
proteins = gv.read_fasta("proteins.fasta")
regions = gv.read_bed("regions.bed")
```

`read_gff()` gives a row per feature, with the nine columns of the format and a column for each attribute. `read_fasta()` gives a row per sequence, with the `key=value` pairs of its header as columns, its `sequence` and, when the header has a location, `start`, `end` and `strand`. `read_bed()` gives 1-based starts, as R's reader does.

Each table goes to `GC()` with the names of its start and end columns:

```python
import geneviewer as gv

genes = gv.read_gff("annotation.gff3")
cds = genes[genes["type"] == "CDS"]
chart = gv.GC(cds, start="start", end="end", strand="strand", height="200px")
```

## Transcripts

[`get_introns()`](./reference/get_introns) adds the introns between the exons of a table of transcripts. [`.transcript()`](./reference/GC-transcript) calls it, so it is only needed to get the table itself.
