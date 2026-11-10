<!-- Made by scripts/export-python-articles.py from articles/python/transcripts.md. Edit that. -->

# Visualizing Gene Transcripts

This tutorial shows how to load transcript data from Ensembl and visualize it using `geneviewer`. As a practical example, we will retrieve the exon and UTR regions of five different splice variants of the BRCA1 gene and display the results with `geneviewer`.

## Loading Transcript data

Transcript data for the BRCA1 gene can be loaded from the [Ensembl REST service](https://rest.ensembl.org/), with the Ensembl gene ID obtained from the Ensembl website. In this example, we look up the gene with its transcripts (`expand=1`) and their UTRs (`utr=1`). The answer holds every transcript of the gene, each with its exons and UTRs.

```python
import json
import urllib.request

import pandas as pd

ensembl_gene_id = "ENSG00000012048"
url = (
    f"https://rest.ensembl.org/lookup/id/{ensembl_gene_id}"
    "?expand=1;utr=1;content-type=application/json"
)
with urllib.request.urlopen(url) as response:
    gene = json.load(response)

transcripts = gene["Transcript"]
```

| ensembl_gene_id | ensembl_transcript_id |
| --- | --- |
| ENSG00000012048 | ENST00000357654 |
| ENSG00000012048 | ENST00000489037 |
| ENSG00000012048 | ENST00000473961 |
| ENSG00000012048 | ENST00000497488 |
| ENSG00000012048 | ENST00000478531 |

The results shown in this article come from the `BRCA1_splice_variants` data set that is included with `geneviewer`. You can use it directly to follow along without connecting to Ensembl: `transcript_attributes = datasets.load("BRCA1_splice_variants")`. Ensembl updates its annotation, so the positions it returns today can differ by a few base pairs from those in the data set.

Now that we have the transcripts of the BRCA1 gene, we can collect the start and end positions of the exons, as well as the 5' and 3' UTRs, with the strand of each transcript. As an example, we only keep five of the transcripts. Each feature becomes a row, with its kind in the `type` column, and the rows are combined into a single DataFrame.

```python
transcript_ids = [
    "ENST00000357654",
    "ENST00000489037",
    "ENST00000473961",
    "ENST00000497488",
    "ENST00000478531",
]
utr_types = {"five_prime_UTR": "5_utr", "three_prime_UTR": "3_utr"}

rows = []
for transcript in transcripts:
    if transcript["id"] not in transcript_ids:
        continue
    features = [("exon", exon) for exon in transcript["Exon"]]
    features += [(utr_types[utr["object_type"]], utr) for utr in transcript.get("UTR", [])]
    for feature_type, feature in features:
        rows.append(
            {
                "ensembl_transcript_id": transcript["id"],
                "type": feature_type,
                "start": feature["start"],
                "end": feature["end"],
                "strand": transcript["strand"],
            }
        )

transcript_attributes = pd.DataFrame(rows)
```

| ensembl_transcript_id | type | start | end | strand |
| --- | --- | --- | --- | --- |
| ENST00000357654 | exon | 43090944 | 43091032 | -1 |
| ENST00000357654 | exon | 43082404 | 43082575 | -1 |
| ENST00000357654 | exon | 43076488 | 43076614 | -1 |
| ENST00000357654 | exon | 43074331 | 43074521 | -1 |
| ENST00000357654 | exon | 43070928 | 43071238 | -1 |
| ENST00000357654 | exon | 43067608 | 43067695 | -1 |

Now that we have the start, end and strand information of the transcripts we can visualize the results using `geneviewer` and the `.transcript()` method. Note that the intron positions are calculated based on the exon positions. To ensure the exons are recognized, the type column with the feature name must be specified and include "exon" in its name.

```python
from geneviewer import GC

GC(
    transcript_attributes,
    start="start",
    end="end",
    strand="strand",
    height="600px",
).transcript(transcript="ensembl_transcript_id", type="type")
```

@chart article-transcripts-1 nocode

We can further customize the chart by adding a title with the transcript name and a footer with the relative abundance of each transcript. To change the color, alter the appearance of specific features, and explore many more options, see the [Get started](/getting-started?lang=py#transcripts) guide or the [`.transcript()`](../reference/GC-transcript) documentation.

```python
(
    GC(transcript_attributes, height="600px")
    .transcript(
        transcript="ensembl_transcript_id",
        strand="strand",
        type="type",
    )
    .cluster_title(
        title=list(transcript_attributes["ensembl_transcript_id"].unique()),
        title_font={"fontSize": "12px"},
    )
    .cluster_footer(
        title=["0.8%", "0.1%", "0.07%", "0.02%", "0.01%"],
        align="center",
    )
)
```

@chart article-transcripts-2 nocode
