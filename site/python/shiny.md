---
prev:
  text: Getting started
  link: /python/
next:
  text: Reference
  link: /python/reference/
---

# Shiny for Python

`geneviewer.shiny` has the output of a chart, its renderer and `zoom_to()`. It needs the `shiny` extra:

```sh
pip install "geneviewer-py[shiny]"
```

## A chart in an app

[`output_geneviewer()`](./reference/output_geneviewer) puts the chart in the page, and a function decorated with [`@render_geneviewer`](./reference/render_geneviewer) returns the chart to draw. When an input the function reads changes, the chart is drawn again in place:

```python
from shiny import App, ui

from geneviewer import GC, datasets
from geneviewer.shiny import output_geneviewer, render_geneviewer

clusters = datasets.load("ophA_clusters")

app_ui = ui.page_fluid(
    ui.input_select("theme", "Theme", ["default", "dark", "vintage"]),
    output_geneviewer("chart", height="300px"),
)


def server(input, output, session):
    @render_geneviewer
    def chart():
        return (
            GC(clusters, cluster="cluster", group="class", height="300px")
            .labels("name")
            .theme(input.theme())
        )


app = App(app_ui, server)
```

## Events

The events switched on with [`.events()`](./reference/GC-events) set inputs named after the output: for the output `"chart"`, a selected gene is `input.chart_select()`.

| Input | Value | Switched on by |
| --- | --- | --- |
| `input.<id>_click()` | The element clicked | `click=True` (the default) |
| `input.<id>_dblclick()` | The element double-clicked | `dblclick=True` |
| `input.<id>_select()` | The element selected last | `select=True` |
| `input.<id>_selection()` | Every selected element, as a list | `select=True` |
| `input.<id>_drag()` | An element moved by dragging, and its offset | `drag=True` |
| `input.<id>_moves()` | The elements a reset, undo or redo moved | `drag=True` |
| `input.<id>_zoom()` | The window of the zoom slider | `zoom=True` |
| `input.<id>_rendered()` | The chart was drawn | `rendered=True` |

Each value is a dict; [Events](/api#events) describes what each holds. An input is set again when the same event happens twice, so a second click on the same gene reaches the server too.

```python
from shiny import App, render, ui

from geneviewer import GC, datasets
from geneviewer.shiny import output_geneviewer, render_geneviewer

clusters = datasets.load("ophA_clusters")

app_ui = ui.page_fluid(
    output_geneviewer("chart", height="300px"),
    ui.output_text("selected"),
)


def server(input, output, session):
    @render_geneviewer
    def chart():
        return (
            GC(clusters, cluster="cluster", group="class", height="300px")
            .labels("name")
            .events(select=True)
        )

    @render.text
    def selected():
        gene = input.chart_select()
        return f"Selected: {gene['data']['name']}" if gene else "Click a gene"


app = App(app_ui, server)
```

## Moving the zoom slider

[`zoom_to()`](./reference/zoom_to) sets the window of a chart with a zoom slider (`.zoom()`) from the server, without drawing the chart again:

```python
from shiny import App, reactive, ui

from geneviewer import GC, datasets
from geneviewer.shiny import output_geneviewer, render_geneviewer, zoom_to

clusters = datasets.load("ophA_clusters")

app_ui = ui.page_fluid(
    ui.input_action_button("first_half", "Zoom to the first half"),
    ui.input_action_button("everything", "Show everything"),
    output_geneviewer("chart", height="300px"),
)


def server(input, output, session):
    @render_geneviewer
    def chart():
        return GC(clusters, cluster="cluster", group="class", height="300px").zoom()

    @reactive.effect
    @reactive.event(input.first_half)
    def _():
        zoom_to("chart", [0, 0.5])

    @reactive.effect
    @reactive.event(input.everything)
    def _():
        zoom_to("chart", None)


app = App(app_ui, server)
```

## Toolbar icons

The toolbar's own icons need nothing. Custom icons, set with [`.toolbar()`](./reference/GC-toolbar), are [Font Awesome](https://fontawesome.com/search?ic=free) icons by name, such as `"camera"`, and need Font Awesome on the page. A Shiny for Python page does not load it, so add it to the UI:

```python
from shiny import ui

font_awesome = ui.head_content(
    ui.tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6/css/all.min.css",
    )
)
```

## An example app

The package's repository has an app with three charts, a panel that shows each event input, and buttons that move the zoom slider:

```sh
git clone https://github.com/nvelden/geneviewer-py
shiny run geneviewer-py/examples/shiny/app.py
```
