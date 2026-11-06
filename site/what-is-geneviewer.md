---
prev: false
next:
  text: Getting started
  link: /getting-started
---

# What is geneviewer?

**geneviewer is a JavaScript library for drawing gene clusters, transcripts and genome alignments in the browser.** You give it a table of genes and say what to draw. It gives you an interactive SVG chart that you can zoom, rearrange and save as a figure.

@chart interactive log

Hover a gene for its tooltip, drag the slider below the clusters to zoom, or click a gene to select it. The box under the chart lists the events your page would receive.

## One spec, one chart

A chart is described by a *spec*: a plain object with the data and one key for each part of the chart. Nothing else is needed to draw it, and there is no chain of calls to learn.

```js
const chart = geneviewer.newChart("#chart", {
  version: 1,
  data: genes,
  fields: { cluster: "cluster", group: "class" },
  labels: { label: "name" },
  links: { data: homologs, measure: "identity" },
  legend: { position: "top" },
  theme: "publication",
});
```

Because a spec is only data, it can be stored as JSON, sent from a server or written by another language, and it draws the same chart wherever it comes from. Change a part of it later with `chart.update()` and the chart draws again.

## What it draws

- **Genes** as arrows or boxes on a sequence line, coloured by group.
- **Transcripts** with their exons, introns and UTRs.
- **Links** between homologous genes or alignment blocks, shaded by identity.
- **Everything around them**: titles, labels, legends, axes, coordinates, scale bars, scale breaks and annotations.

The [examples](/examples) show what these look like together, and [getting started](/getting-started) goes through each part with a chart and its code.

## What it does not do

geneviewer only draws charts. It does not read GenBank or GFF files, align proteins or genomes, or work out which genes are homologous: its input is tables that already hold those results.

That work belongs to the languages around the library. The R package reads the files and runs the alignments, then hands the library a spec. If you already have your data in tables, or your page gets them from a server, the library is all you need.

It is also not a genome browser. It has no reference tracks and does not load data as you scroll. It is made for the region you want to show, from a few genes to a set of whole plasmids.

## Using it from other languages

The same charts can be made without writing JavaScript:

- **R:** the [geneviewer package](https://nvelden.github.io/geneviewer/) builds charts from data frames and from GenBank, GFF, FASTA and BED files. Version 0.3.0, in development, draws them with this library. The R code next to each chart on this site is for that version.
- **In the browser, without code:** the [Gene Cluster Dashboard](https://nvelden.github.io/geneviewer-shinylive/) loads CSV, GenBank and FASTA files and lets you design a chart by point and click.
- **Python:** a package for Jupyter and Shiny for Python is planned, built on the same library. See the [roadmap](https://github.com/nvelden/geneviewer-js/blob/main/docs/roadmap.md).

## Built on D3

geneviewer draws with [D3](https://d3js.org), and D3 is included in the script tag build. The colour schemes, number formats and symbols of D3 can be used by name in a spec, such as `colorScheme: "schemeSet2"` or `ticksFormat: ".2s"`. You do not need to know D3 to use geneviewer.
