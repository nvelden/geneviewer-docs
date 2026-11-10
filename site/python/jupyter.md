---
prev: false
next:
  text: Shiny
  link: /python/shiny
---

# Jupyter notebooks

With the `jupyter` extra, charts are drawn in notebooks:

```sh
pip install "geneviewer-py[jupyter]"
```

The charts are [anywidget](https://anywidget.dev/) widgets, so they work in JupyterLab, Jupyter Notebook, VS Code, Google Colab and marimo.

## A chart in a cell

A cell that ends with a chart draws it below the cell:

@chart python-first-chart

The chart is the live chart of the other pages of this site: hover a gene for its tooltip, and the chart for the button that saves it as SVG or PNG.

## Events

To read what happens in a chart, keep it as a widget with [`.widget()`](./reference/GC-widget). The events switched on with [`.events()`](./reference/GC-events) set attributes of the widget:

@chart python-jupyter-widget

After a click on a gene, a later cell can read it:

```python
widget.select["data"]["name"]
```

| Attribute | Value | Switched on by |
| --- | --- | --- |
| `widget.click` | The element clicked | `click=True` (the default) |
| `widget.dblclick` | The element double-clicked | `dblclick=True` |
| `widget.select` | The element selected last | `select=True` |
| `widget.selection` | Every selected element, as a list | `select=True` |
| `widget.drag` | An element moved by dragging, and its offset | `drag=True` |
| `widget.moves` | The elements a reset, undo or redo moved | `drag=True` |
| `widget.zoom` | The window of the zoom slider | `zoom=True` |
| `widget.rendered` | The chart was drawn | `rendered=True` |

Each is `None` until its event happens, and then a dict (a list for `selection`); [Events](/api#events) describes what each holds. These are the values a Shiny app gets as `input.<id>_<event>()`.

[`widget.on()`](./reference/GCWidget-on) calls a function at each event, also when the same event happens twice:

```python
selected = []
widget.on("select", selected.append)
```

## Moving the zoom slider

[`widget.zoom_to()`](./reference/GCWidget-zoom_to) sets the window of a chart with a zoom slider (`.zoom()`), without drawing the chart again. `None` shows everything:

```python
widget.zoom_to([0, 0.5])
widget.zoom_to(None)
```

With `.events(zoom=True)`, `widget.zoom["range"]` is the window the reader picked, which can go back into `zoom_to()`.

## Drawing another chart

Setting `widget.chart` draws another chart in the same place, for example the same data with another theme:

```python
widget.chart = widget.chart.theme("dark")
```

## Toolbar icons

The toolbar's own icons need nothing. Custom icons, set with [`.toolbar()`](./reference/GC-toolbar), are [Font Awesome](https://fontawesome.com/search?ic=free) icons by name and need Font Awesome on the page. JupyterLab does not load it, so load it in a cell:

```python
from IPython.display import HTML

HTML(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/'
    '@fortawesome/fontawesome-free@6/css/all.min.css">'
)
```
