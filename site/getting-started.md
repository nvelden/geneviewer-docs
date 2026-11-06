---
prev:
  text: What is geneviewer?
  link: /what-is-geneviewer
next:
  text: Examples
  link: /examples
---

# Getting started

Every chart on this page is drawn live from the code below it. The **R** tab has the same chart in the [geneviewer R package](https://nvelden.github.io/geneviewer/).

## Installation

Load geneviewer from a CDN, or install it from npm for a bundler such as Vite or webpack:

::: code-group

```html [Script tag]
<script src="https://cdn.jsdelivr.net/npm/geneviewer-js@0.3/dist/geneviewer.min.js"></script>
```

```html [ES module]
<script type="module">
  import { newChart } from "https://cdn.jsdelivr.net/npm/geneviewer-js@0.3/dist/geneviewer.standalone.mjs";
</script>
```

```sh [npm]
npm install geneviewer-js
```

```sh [yarn]
yarn add geneviewer-js
```

```sh [pnpm]
pnpm add geneviewer-js
```

:::

The script tag defines the global `geneviewer` and includes D3. With npm, import the functions you need. That build imports `d3` from npm, so a project that already uses D3 loads it once:

```js
import { newChart } from "geneviewer-js";
```

The library adds its styles to the page with the first chart, and TypeScript types are included.

## Your first chart

A chart is drawn into an element, which sets its size, from a spec: the data and what to draw. Copy this into an HTML file and open it:

```html
<div id="chart" style="height: 150px"></div>
<script src="https://cdn.jsdelivr.net/npm/geneviewer-js@0.3/dist/geneviewer.min.js"></script>
<script>
  const genes = [
    { name: "ophB1", start: 2522, end: 4276, class: "Monooxygenase" },
    { name: "ophC", start: 5286, end: 4718, class: "NTF2-like" },
    { name: "ophA", start: 9536, end: 10904, class: "Methyltransferase" },
    { name: "ophD", start: 12616, end: 11859, class: "O-acyltransferase" },
    { name: "ophB2", start: 13183, end: 15046, class: "Monooxygenase" },
    { name: "ophP", start: 19346, end: 16016, class: "Prolyloligopeptidase" },
    { name: "ophE", start: 20170, end: 21484, class: "F-box/RNHI-like" },
  ];

  const chart = geneviewer.newChart("#chart", {
    version: 1,
    data: genes,
    fields: { group: "class" },
  });
</script>
```

@chart guide-single-gene-cluster nocode

## Data and fields

`data` is the gene table: an array of rows, as above, or an object of columns (`{ start: [...], end: [...] }`). `fields` names the columns the chart uses:

- `start` and `end`: the gene's positions (default: the columns `start` and `end`). A gene whose start is after its end is on the reverse strand.
- `cluster`: which cluster a gene is in. Without it, all genes are one cluster.
- `group`: colours the genes and fills the legend.
- `strand`: `1`, `forward`, `+` or `sense`; `-1`, `0`, `reverse`, `-`, `antisense` or `complement`.

Other columns can be used in labels, tooltips and styles.

The charts below share three tables from the R package, the omphalotin gene clusters of two fungi. Add them to your page to run the code:

@tables

## Cluster visualization

### Single gene cluster

The minimum is the start and end of each gene. A `group` column is used for the colours and the legend.

@chart guide-single-gene-cluster

### Multiple gene clusters

For several clusters, name the column that tells them apart in `fields.cluster`. Clusters share the height of the element, so here each of the two gets 150px.

@chart guide-multiple-gene-clusters

### Styling

The `style` key takes CSS for the chart as a whole. The other parts of the chart each have their own options, shown below.

@chart guide-styling

## Updating

`update()` merges a partial spec into the chart's spec and draws again. Tables (`data`, `links.data`) are replaced whole. `setSpec()` replaces the spec, and `getSpec()` returns it.

```js
chart.update({ title: { title: "OphA clusters" }, theme: "dark" });
chart.update({ data: moreGenes });
const spec = chart.getSpec();
```

Call `chart.resize()` when the element changes size, and `chart.destroy()` to remove the chart and its listeners.

## Events

Charts report what the mouse does when you ask for it with the `events` key. Each kind of interaction has its own option:

| Option | What it does |
|---|---|
| `click` | Reports a click: the part of the chart (`"genes"`, `"labels"`, `"links"`, `"scale"`, `"clusterTitle"`, ...), its cluster and the data of the clicked gene, link or legend group. |
| `select` | A click selects a gene, label, coordinate, legend label or marker, the scale, or the title or subtitle of a cluster title, footer or label, and outlines it. Shift-, Ctrl- or Cmd-click and a box drawn on empty space select several. A click elsewhere or Escape ends the selection. |
| `drag` | Elements can be moved with the mouse and the arrow keys, and moves undone. See [Moving elements](#moving-elements). |
| `zoom` | Reports the window of the zoom slider. See [Zoom](#zoom). |
| `dblclick` | Reports double-clicks. Enter opens a selected element. |
| `highlight` | Outlines the part of the chart under the mouse. |
| `legendClick` | Whether clicks on the legend are reported. Hiding and showing groups in the legend always works. |
| `rendered` | Reports each finished draw. |

Listen with `on()`, which gives a function that stops listening. Each event is also a `geneviewer:<name>` DOM event on the element.

```js
chart.update({ events: { click: true, select: true } });

const stop = chart.on("select", (event) => console.log(event.detail));

document.getElementById("chart")
  .addEventListener("geneviewer:click", (event) => console.log(event.detail));
```

Handlers that should also get the events of the first draw go in the options of `newChart()`:

```js
geneviewer.newChart("#chart", spec, {
  on: { rendered: (event) => console.log("drawn", event.detail) },
});
```

Select from code, and read the selection back. The detail of a selected element also has `style`: how it is drawn (its colour, size, font, ...), for example to show the current values in an editor.

```js
chart.select([{ component: "genes", data: { rowID: 3 } }]);
const selected = chart.getSelection();
```

Click a gene, label or cluster title in this chart to select it:

@chart guide-click-interactions

## Moving elements

With `events: { drag: true }` you can arrange a chart with the mouse, for example to move a label away from a gene or the legend to an empty corner before saving a figure. Gene labels, the chart title and subtitle, the titles, footers and labels of the clusters, the scale axis and scale bar (each as a whole) and the labels and markers of the legend (each on its own) can be moved. Try it in the chart below:

- **Drag** an element to move it. A press without moving is still a click.
- **Shift-, Ctrl- or Cmd-click** adds an element to the selection, or takes it out again. **Drag on empty space** to draw a box: the elements entirely inside it are selected, such as all items of the legend. Dragging one of the selected elements moves them all.
- **Arrow keys** move the selected elements by a pixel, or 10 pixels with Shift.
- **Undo, redo and reset** appear next to the download icon once something has moved. Reset moves everything back to where it was first drawn. After clicking the chart, Ctrl+Z (Cmd+Z on a Mac) undoes and Ctrl+Shift+Z or Ctrl+Y redoes, as do `chart.undo()` and `chart.redo()`.
- **Escape** cancels a drag, or ends the selection.

@chart guide-moving-elements

Moved elements are part of the saved SVG and PNG. A move is kept until the page is loaded again. To keep it in the spec, give its offset in pixels, `moveX` (right) and `moveY` (down), in `elementStyle`. Elements are identified as they are for [styling](#individual-items): a gene label by its row, a cluster title, footer or label by its cluster and part, the scale and scale bar by their cluster, and a legend label or marker by its group and part.

@chart guide-moving-elements-2

The `drag` event reports each move of one element, with its new `position` (`moveX` and `moveY`) and the `action` (`"drag"`, `"nudge"`, `"undo"` or `"redo"`). A move of several elements at once, such as a reset, is reported once by `moves`, with the `action` and a list of `moves`. Store these and add them to `elementStyle` to keep the moves when the chart is drawn again.

## Toolbar

The undo, redo and reset icons, the reset zoom icon of the zoom slider and the save button make up the toolbar. The `toolbar` key sets when it shows (`"hover"`, `"always"`, for example for touch screens, or `"never"`), its corner, which buttons it has, the size and colours of its icons and the look of its tooltips. The icons are [Font Awesome](https://fontawesome.com/search?ic=free) icons, by name, such as `"camera"`, or by their classes for another style, such as `"fa-regular fa-floppy-disk"`.

@chart guide-toolbar

The built-in themes style the toolbar to fit, and a theme of your own can set it as a component: `theme: { toolbar: { color: "grey", hoverColor: "black" } }`. The `toolbar` key takes precedence over the theme.

## Selections

### Specific clusters

Options apply to all clusters of the chart by default. A part can also be an array of entries, and an entry with `clusters` applies only to those clusters. Name a cluster or give its number, starting at 1.

Here the labels of the first cluster are moved below the genes:

@chart guide-specific-clusters

### Individual items

To style one item of a cluster, use `itemStyle`, a list with the index of the item and its styles. The index starts at 0.

Here the 3rd label of the ophA cluster is red and bold. In cluster 2 the 5th label is red and bold as well, and the 4th label is moved.

@chart guide-individual-items

`elementStyle` styles one element at a time, without the index: a gene, label or coordinate by its row in the data (`rowID`), or the title or subtitle of a cluster title, footer or label by its `cluster` and `part`. Its options add to the other styles of the chart. Legend labels and markers are styled by their `group` and `part`. These are the same names the selection events report, so an editor built on them can record its changes here.

@chart guide-individual-items-2

## Layout

### Cluster

The `cluster` key styles clusters and sets their margins. Here each cluster has its own background, and the left and right margins are 25px. The margins of the title and legend do not change. To change those too, use [`grid`](#grid).

@chart guide-cluster

### Separate forward and reverse strands

Forward and reverse strands can go on separate tracks. `strandSpacing` sets the space between them.

@chart guide-separation-of-forward-and-reverse-strands

### Prevent gene overlap

With `preventGeneOverlap: true`, genes that overlap go on separate tracks, below each other. A gene goes on the first track where it overlaps no gene placed before it, and `overlapSpacing` sets the space between the tracks. Here the overlapping HOX genes are 30 pixels apart. Setting both `separateStrands` and `preventGeneOverlap` is not supported at the moment.

@chart guide-prevent-gene-overlap

With `preventGeneOverlap: "nested"` only the genes that lie inside another gene, such as an ORF in another reading frame, go on the tracks below. All other genes stay on the first track, also where they overlap. `styleBy: "geneTrack"` styles the genes of each track, here to draw the nested ORFs of SARS-CoV-2 smaller.

@chart guide-prevent-gene-overlap-2

### Grid

The `grid` key sets the grid of the chart or of specific clusters. Here the top and bottom margins are larger, and the left and right margins go from the default 50px to 25px.

@chart guide-grid

Clusters can be side by side with `direction: "row"` and a `width` for each cluster.

@chart guide-grid-2

## Genes

The `genes` key styles the genes and takes any CSS style. The colours come from `fields.group`. To change them, use the [`color` key](#colors), which changes the genes and the legend together.

@chart guide-genes

Genes are arrows by default. Set `marker` to `arrow`, `boxarrow`, `box`, `cbox` or `rbox`, and `markerSize` to `small`, `medium` (the default) or `large`.

@chart guide-genes-2 nocode
@chart guide-genes-3 nocode
@chart guide-genes-4 nocode
@chart guide-genes-5 nocode
@chart guide-genes-6

For finer control, `markerHeight` overrides `markerSize`, and `x` and `y` move the markers. The `arrow` and `boxarrow` markers also have `arrowheadWidth` and `arrowheadHeight`.

@chart guide-genes-7

`groupStyle` styles all genes of a group at once, with the same options as `itemStyle`.

@chart guide-genes-8

## Gene alignment

The `align` key aligns one gene across clusters: each cluster's scale is set so the gene is at the same place in every cluster. Name the column with the identifiers in `idColumn`, and the gene in `id`. The identifier must be the same across clusters and unique within each.

@chart guide-gene-alignment

## Transcripts

The `transcript` key draws transcripts. It needs a column with an ID for each transcript and a `type` column that says whether the feature is a UTR or an exon. A `strand` column sets the direction. Introns are worked out from the exon positions.

@chart guide-transcripts

Group by `type` and use `customColors` to colour each kind of feature. Junctions can be added with the [arc annotation](#arc).

@chart guide-transcripts-2

Introns, exons, UTRs and labels are styled with `styleIntrons`, `styleExons`, `styleUTRs` and `labelOptions`.

@chart guide-transcripts-3

`itemStyleExons`, `itemStyleIntrons` and `itemStyleUTRs`, with `selection`, style individual features of a specific transcript.

@chart guide-transcripts-4

## Links

The `links` key connects genes or regions of different clusters. Its `data` is a table with the positions of both ends and their clusters (`start1`, `end1`, `cluster1`, `start2`, `end2`, `cluster2`). The JavaScript library draws the links you give it and does not work out which genes match: in R, `GC_links()` makes this table from a column of the genes.

@chart guide-links

A table can link only the genes you want:

@chart guide-links-2

An `identity` or `similarity` column sets the colour intensity of the links when you name it in `measure`. `linkStyle`, `labelStyle` and `linkWidth` style the links and their labels, and `colorBarOptions` the colour bar.

@chart guide-links-3

Links can also join any regions, rather than genes. They run from nearly white at a measure of `vmin` to the full colour at `vmax` (0 and 100 by default), which are also the ends of the colour bar. Setting `vmin` to the lowest measure spreads the colours over the data. Measures below `vmin` or above `vmax` get the colour of that end.

@chart guide-links-4

With `labelPosition: "link"` the measure is written in the middle of each link where it fits. The `position` of `colorBarOptions` moves the colour bar to another corner or, with `"legend"`, into the legend.

@chart guide-links-5

## Sequence

The `sequence` key styles the line the genes sit on, with `lineStyle`, and its scale break markers, with `markerStyle`.

@chart guide-sequence

## Labels

Each cluster can have a title, gene labels, a cluster label and a footer.

@chart guide-labels

Use `x`, `y` and `align` to place labels. Here `labels` has two entries: the first sets labels for all clusters, and the second moves the 4th and 8th label of cluster 2 so they do not overlap. The index starts at 0.

@chart guide-labels-2

`itemStyle` also sets the style of those labels:

@chart guide-labels-3

Labels that overlap another label are turned by default. `adjustLabels: "hide"` hides them instead, until there is room for them, such as when zoomed in.

### Spread labels

`adjustLabels: "spread"` puts the labels on one line below the lowest gene, as in gene order figures. Labels that would overlap are moved apart, and a line goes from each label to its gene.

@chart guide-spread-labels

`spreadPosition: "top"` puts the labels above the highest gene instead. `leaderLine` sets the distance from the genes to the labels (`length`, in pixels, default 20) and the style of the lines, and `leaderLine: false` spreads the labels without lines.

@chart guide-spread-labels-2

## Annotations

The `annotation` key adds annotations to clusters: `text`, `textMarker`, `line`, `arrow`, `symbol`, `rectangle`, `arc`, `promoter` and `terminator`. Several annotations of one type can be placed with arrays of values. With `trackMouse: {}` the chart shows the position under the mouse, which makes it easier to find `x` and `y`.

@chart guide-annotations

### Text

All the options of a text annotation. `text`, `x` and `y` can also be arrays.

@chart guide-text

### Text marker

All the options of a text marker. All but the styles can also be arrays. `x1` and `x2` are unset by default, and `position` is used for the horizontal placement.

@chart guide-text-marker

### Promoter and terminator

All the options of a promoter, or a terminator with `type: "terminator"`. All but the styles can also be arrays.

@chart guide-promoter-terminator

### Symbol

All the options of a symbol: `circle`, `cross`, `diamond`, `square`, `star`, `triangle` or `wye`. All but the styles can also be arrays.

@chart guide-symbol

### Arrow

All the options of an arrow. All but the styles can also be arrays.

@chart guide-arrow

### Line

All the options of a line. All but the styles can also be arrays.

@chart guide-line

### Arc

All the options of arcs, here for the junctions of a transcript.

@chart guide-arc

### Rectangle

All the options of a rectangle. `rotation` can also be an array.

@chart guide-square

## Colors

The `color` key sets the colours of the legend and genes, with `colorScheme` or `customColors`.

### colorScheme

A color scheme by name, such as `"schemeCategory10"` or `"schemeAccent"` from D3.

@chart guide-colorscheme

`schemeCategory10`: ten categorical colours.

@chart guide-colorscheme-2 nocode

`schemeAccent`: eight categorical colours.

@chart guide-colorscheme-3 nocode

`schemeDark2`: eight categorical colours.

@chart guide-colorscheme-4 nocode

`schemePaired`: twelve categorical colours.

@chart guide-colorscheme-5 nocode

`schemePastel1`: nine categorical colours.

@chart guide-colorscheme-6 nocode

`schemePastel2`: eight categorical colours.

@chart guide-colorscheme-7 nocode

`schemeSet1`: nine categorical colours.

@chart guide-colorscheme-8 nocode

`schemeSet2`: eight categorical colours.

@chart guide-colorscheme-9 nocode

`schemeSet3`: twelve categorical colours.

@chart guide-colorscheme-10 nocode

`schemeTableau10`: ten categorical colours, originally created for Tableau.

@chart guide-colorscheme-11 nocode

### customColors

`customColors` sets the colour of each group: an array of colours, or an object from group to colour.

An array of colours:

@chart guide-customcolors

An object from group to colour:

@chart guide-customcolors-2

## Patterns

Journals sometimes ask for figures in black and white. The `pattern` key fills the genes, exons and legend markers with a pattern for each group instead of a colour. By default each group gets the next pattern from a fixed list, in black on a white background.

@chart guide-patterns

There are 16 patterns. Without `patterns`, the groups get them in the order shown below, which keeps patterns that look alike (such as `diagonal` and `wideStripes`) far apart. `none` is not used by default.

@chart guide-patterns-2

Use `patterns` to choose them: an array is recycled over the groups, and an object sets the pattern for each group.

@chart guide-patterns-3

With many groups, combine the patterns with grey backgrounds. The `background` array is recycled in the same way, so 3 patterns and 2 greys give 6 different fills. `color` sets the colour of the lines and dots, `size` the width of one pattern tile and `strokeWidth` the width of the lines.

@chart guide-patterns-4

Set `background: null` to draw the patterns on top of the gene colours. Each group then has both a colour and a pattern, which also helps readers who cannot tell some colours apart.

@chart guide-patterns-5

Like `background`, `color` can be an array or an object, so some groups can have white patterns on black. `inverseDots` draws the dots in the background colour on a tile filled with `color`.

@chart guide-patterns-6

## Themes

The `theme` key sets the default look of the whole chart at once: fonts, text and line colours, the background, the gene colours and the options of each part. There are 7 built-in themes:

- `"default"`: the default look of geneviewer.
- `"classic"`: the default theme of ECharts 5.
- `"dark"`: light text and soft colours on a dark background.
- `"vintage"`: muted colours on a cream background.
- `"infographic"`: strong colours.
- `"publication"`: for journal figures (Arial, 7 pt text, black text and axes, italic gene labels and colour-blind safe colours).
- `"bw"`: black and white, with a pattern for each group.

@chart guide-themes
@chart guide-themes-2
@chart guide-themes-3
@chart guide-themes-4

A theme only changes how things look. It does not add parts to the chart: a scale still needs the `scale` key and labels the `labels` key.

Each built-in theme also styles the toolbar. Hover the chart below and drag a label to see the undo icon in the dark theme.

@chart guide-themes-5

### Global settings

Next to `base`, the name of a built-in theme, `theme` takes settings for all parts: `fontFamily`, `textColor`, `lineColor` (the sequence line, axis, coordinates and scale bar), `background`, `palette` (the gene colours) and `pattern`.

@chart guide-global-settings

`palette` takes an array of colours, the name of a D3 colour scheme (such as `"schemeSet2"`) or the name of a geneviewer palette: `okabeIto`, `classic`, `vivid`, `dark`, `vintage`, `infographic`, `greys` or `blues`. The geneviewer palettes can also be used as the `colorScheme` of `genes`, `transcript` and `color`.

### Text size

`textScale` scales all text of the chart at once, for example for a slide or a figure that is printed small. The title and the width of the cluster labels grow with the text.

@chart guide-text-size

### Component options

Options for a single part are given under its own name, such as `labels: { fontSize: "10px" }` or `links: { curve: false }`.

@chart guide-component-options

Options set on a part always take precedence over the theme. Below the gene labels stay 14px, although the theme sets them to 10px.

@chart guide-component-options-2

## Legend

The `legend` key shows, hides and styles the legend, which is at the bottom by default. Here it is with all its default settings.

@chart guide-legend

Here the order, size, position and look of the legend are changed. The `color` key changes the colours of the legend and genes together.

@chart guide-legend-2

## Scale

The `scale` key sets the scale of the chart. `padding` adds space at the start and end of the cluster, `hidden` hides the axis, and `y` sets its position (1 at the bottom, 100 at the top).

@chart guide-scale

### Automatic scale breaks

`autoBreaks`, `autoBreakThreshold` and `breakPadding` deal with widely spaced genes. `autoBreaks: true` adds breaks in the scale to avoid long empty stretches. `autoBreakThreshold` is the share of the cluster's range an empty stretch must exceed, and `breakPadding` the padding around a break.

Here a break is added where the space between genes exceeds 20% of the cluster's range, with 1% padding on both sides.

@chart guide-automatic-scale-breaks

### Manual scale adjustments

By default the scale runs from the lowest to the highest position of the genes. `start` and `end` change this, and `breaks` adds breaks by hand. Here the range is set by hand and a break removes the long stretch between gene 2 and gene 3.

@chart guide-manual-scale-adjustments

### Reverse scale

`reverse: true` reverses the scale.

@chart guide-reverse-scale

### Shared genomic scale

`axisType: "range"` gives the clusters one scale, from 0 to the widest span among them, rather than their own genomic coordinates. Some options, such as breaks and a reversed scale, may no longer work on a shared axis.

@chart guide-shared-genomic-scale

### Scale styling

`tickStyle`, `textStyle` and `lineStyle` take CSS styles. `ticksCount` sets the number of ticks, or `tickValues` the ticks themselves. `ticksFormat` sets how the numbers are written (see [d3-format](https://d3js.org/d3-format)).

@chart guide-styling-2

## Zoom

The `zoom` key adds a slider below the clusters to zoom in on part of them. Drag a handle to change the window, drag the window to move it, and click the track to move the window there. Double-click the slider, or use the reset zoom icon in the toolbar, to show everything again. With the keyboard, the arrow keys move a focused handle or the window (Shift: in bigger steps). The slider shows the genes of each cluster in their colours, and genes, labels, links and the axis follow the window. `range` sets the window shown first:

@chart guide-zoom

By default every cluster zooms to the same share of its own range, which suits clusters of different genomes. With `mode: "absolute"` the window is in base pairs and every cluster shows the same positions. `update: "release"` draws the chart only when the slider is let go, for large charts, and `height`, `overview`, `color`, `style`, `windowStyle` and `handleStyle` set the look of the slider.

@chart guide-zoom-2

With `events: { zoom: true }` the `zoom` event reports the window, on the first draw and after every change. `chart.zoomTo()` moves the window from code, and `null` shows everything again:

```js
chart.on("zoom", (event) => console.log(event.detail.range));
chart.zoomTo([0, 0.5]);
chart.zoomTo(null);
```

## Coordinates

The `coordinates` key shows the positions of the genes. Coordinates that overlap are moved to the top axis, and `overlapThreshold` (default 20) sets when.

@chart guide-coordinates

`tickStyle` and `textStyle` style the ticks and text. The scale itself is set with the `scale` key: to reverse it and show only the coordinates, hide it there.

@chart guide-coordinates-2

The start and end of each gene are shown by default. `tickValuesTop` and `tickValuesBottom` set your own values, and `ticksFormat` how they are written (see [d3-format](https://d3js.org/d3-format)).

@chart guide-coordinates-3

## Scale bar

The `scaleBar` key adds a scale bar. `title` is its label and `unit` its length in base pairs.

@chart guide-scalebar

`x`, `y` and `labelStyle` place and style the label, and `lineStyle` and `tickStyle` style the bar.

@chart guide-scalebar-2

## Tooltip

The tooltip shows the start and end of a gene by default. Set your own text with `formatter`, where a column in braces is replaced by its value. Here it also shows the `name` column.

@chart guide-tooltip

## Saving charts

Hover the chart and then the download icon, and choose **Save as SVG** for a vector image that can be edited in Inkscape or Illustrator and scaled for publications, or **Save as PNG** for an image at screen resolution (make the chart larger for a larger PNG). Elements moved in the chart are saved where they are. A zoomed chart is saved as it shows, without the zoom slider.

From code:

```js
const svg = chart.toSVG();          // text
const png = await chart.toPNG();    // a Blob
await chart.download("png", "clusters.png");
```

Pass `saveAs(blob, filename)` to the options of `newChart()` to save files your own way.

## From R and Python

The JavaScript library only draws. These steps of the [R package](https://nvelden.github.io/geneviewer/) work on the data before it reaches the chart, so in JavaScript you pass their results as tables:

- **Reading files:** [GenBank](https://nvelden.github.io/geneviewer/articles/LoadGenBankFiles.html), [GFF](https://nvelden.github.io/geneviewer/articles/LoadGFF.html) and [FASTA](https://nvelden.github.io/geneviewer/articles/LoadFastaFiles.html).
- **Protein alignment:** [cluster comparison with protein alignments](https://nvelden.github.io/geneviewer/articles/BLASTP.html).
- **Genome alignment:** [MUMmer alignments](https://nvelden.github.io/geneviewer/articles/MUMMER.html).
- **Normalizing:** `GC_normalize()` spaces the genes of a cluster evenly and changes their positions.
- **Matching genes for links:** `GC_links()` makes the link table from a column of the genes.
