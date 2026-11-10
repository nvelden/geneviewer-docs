---
prev: false
next:
  text: Getting started
  link: /getting-started
---

# What is geneviewer?

**geneviewer draws gene clusters, transcripts and genome alignments in the browser, from JavaScript, R or Python.** You give it a table of genes and say what to draw. It gives you an interactive SVG chart that you can zoom, rearrange and save as a figure.

@chart interactive log

Hover a gene for its tooltip, drag the slider below the clusters to zoom, or click a gene to select it. The box under the chart lists the events [[your page||a page or app||a page or app]] would receive.

## One spec, one chart

<div class="lang-r">

In R, `GC_chart()` starts a chart from a data frame and each `GC_` function adds a part to it:

```r
GC_chart(ophA_clusters, group = "class", cluster = "cluster") %>%
  GC_labels("name") %>%
  GC_links("class", measure = "identity") %>%
  GC_legend(position = "top") %>%
  GC_theme("publication")
```

These calls build a *spec*, the plain description of the chart that the JavaScript library draws, so a chart looks and behaves the same from either language.

</div>

<div class="lang-py">

In Python, `GC()` starts a chart from a pandas DataFrame and each method adds a part to it:

```python
(
    GC(ophA_clusters, group="class", cluster="cluster")
    .labels("name")
    .links("class", measure="identity")
    .legend(position="top")
    .theme("publication")
)
```

These calls build a *spec*, the plain description of the chart that the JavaScript library draws, so a chart looks and behaves the same from any of the languages.

</div>

<div class="lang-js">

A chart is described by a *spec*: a plain object with the data and one key for each part of the chart. Nothing else is needed to draw it, and there is no chain of calls to learn.

```js
const chart = geneviewer.newChart("#chart", {
  data: genes,
  fields: { cluster: "cluster", group: "class" },
  labels: { label: "name" },
  links: { data: homologs, measure: "identity" },
  legend: { position: "top" },
  theme: "publication",
});
```

Because a spec is only data, it can be stored as JSON, sent from a server or written by another language, and it draws the same chart wherever it comes from. Change a part of it later with `chart.update()` and the chart draws again.

</div>

## What it draws

- **Genes** as arrows or boxes on a sequence line, coloured by group.
- **Transcripts** with their exons, introns and UTRs.
- **Links** between homologous genes or alignment blocks, shaded by identity.
- **Everything around them**: titles, labels, legends, axes, coordinates, scale bars, scale breaks and annotations.

The [examples](/examples) show what these look like together, and [getting started](/getting-started) goes through each part with a chart and its code.

## What it does not do

<div class="lang-js">

The JavaScript library only draws charts. It does not read GenBank or GFF files, align proteins or genomes, or work out which genes are homologous: its input is tables that already hold those results.

That work belongs to the languages around the library. The R package reads the files and runs the alignments, then hands the library a spec. If you already have your data in tables, or your page gets them from a server, the library is all you need.

</div>

<div class="lang-r">

The drawing is done by the JavaScript library. The R package does the work before it: it reads the files, runs the alignments and hands the library a spec. See [Preparing data](/getting-started#preparing-data).

</div>

<div class="lang-py">

The drawing is done by the JavaScript library. The Python package does the work before it: it reads the files, runs the alignments and hands the library a spec. See [Reading files](/python/reading-files) and [Alignment](/python/alignment).

</div>

geneviewer is not a genome browser. It has no reference tracks and does not load data as you scroll. It is made for the region you want to show, from a few genes to a set of whole plasmids.

## Languages and tools

The same charts can be made in several ways:

- **JavaScript:** the `geneviewer-js` library, from npm or a CDN.
- **R:** the [geneviewer package](/r/reference/) builds charts from data frames and from GenBank, GFF, FASTA and BED files. Version 0.3.0, in development, draws them with the JavaScript library. The R code next to each chart on this site is for that version.
- **In the browser, without code:** the [Gene Cluster Dashboard](https://nvelden.github.io/geneviewer-shinylive/) loads CSV, GenBank and FASTA files and lets you design a chart by point and click.
- **Python:** the [geneviewer-py package](/python/) builds the same charts from pandas DataFrames and from GenBank, GFF, FASTA and BED files, and shows them in Shiny for Python.

## Built on D3

geneviewer draws with [D3](https://d3js.org), and D3 is included in the script tag build. The colour schemes, number formats and symbols of D3 can be used by name, such as [[`colorScheme: "schemeSet2"` or `ticksFormat: ".2s"`||`colorScheme = "schemeSet2"` or `ticksFormat = ".2s"`||`color_scheme="schemeSet2"` or `ticks_format=".2s"`]]. You do not need to know D3 to use geneviewer.
