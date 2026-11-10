---
prev: false
next:
  text: Jupyter notebooks
  link: /python/jupyter
---

# geneviewer for Python

The Python package builds the same charts as the R package and the JavaScript library, from pandas data frames, and shows them in [Jupyter notebooks](./jupyter) and in [Shiny for Python](./shiny). It reads GenBank, GFF, FASTA and BED files and aligns clusters, as the R package does: the articles in the sidebar go through each, from [GenBank files](./articles/genbank) to [a published figure](./articles/published-figure).

These pages describe version 0.1.0.

## Installation

```sh
pip install "geneviewer-py[jupyter]"
```

The distribution is `geneviewer-py` and the import name is `geneviewer`. It needs Python 3.11 or later and pandas. The extras add what a part of the package needs:

| Extra | For |
| --- | --- |
| `jupyter` | Charts in Jupyter notebooks |
| `shiny` | Charts in Shiny for Python |
| `align` | `protein_blast()`, which aligns with Biopython |

## Your first chart

`GC()` makes a chart from a table of genes: a pandas DataFrame with a row per gene and a column for its start and its end. This uses the `ophA_clusters` dataset of the package:

@chart python-first-chart

In a [Jupyter notebook](./jupyter), a cell that ends with the chart draws it. In a Shiny app, an output draws it. This is the whole app for the chart above; save it as `app.py` and run `shiny run app.py`:

```python
from shiny import App, ui

from geneviewer import GC, datasets
from geneviewer.shiny import output_geneviewer, render_geneviewer

clusters = datasets.load("ophA_clusters")
ophA = clusters[clusters["cluster"] == "ophA"]

app_ui = ui.page_fluid(output_geneviewer("chart", height="150px"))


def server(input, output, session):
    @render_geneviewer
    def chart():
        return GC(ophA, group="class", height="150px")


app = App(app_ui, server)
```

[Shiny for Python](./shiny) has the events a chart reports and how to move its zoom slider from the server.

## Adding to a chart

Each method of a chart adds a part or changes one, and returns a new chart, so the calls are chained. With `cluster`, each cluster gets its own row:

@chart python-methods

The methods are the `GC_` functions of the R package under Python names: `GC_clusterLabel()` is `.cluster_label()`, and its argument `titleFont` is `title_font`. The [reference](./reference/) describes each method.

The [guide](/getting-started?lang=r) explains every part of a chart with live examples in R and JavaScript. What it says about an R function holds for the Python method of the same name. Options that take a list in R take a dict in Python, with the names the guide uses:

@chart python-theme

`chart.to_spec()` returns the chart as the spec the JavaScript library draws: a dict that can be written as JSON and drawn on any web page with [`geneviewer.newChart()`](/api).

## Example datasets

The package has the 11 datasets of the R package, as pandas DataFrames:

```python
from geneviewer import datasets

datasets.names()
transcripts = datasets.load("BRCA1_splice_variants")
```

The [reference](./reference/#datasets) lists them. A table of exons and UTRs is drawn as transcripts with `.transcript()`, which adds the introns:

@chart python-transcripts

## Differences from the R package

The charts are the same: both packages write the same spec, and the Python package is tested against the specs the R package makes. The file readers give the same tables as R's. `protein_blast()` can give slightly different identities for some protein pairs, where several alignments are equally good.
