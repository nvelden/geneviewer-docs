# geneviewer-docs

The documentation site of geneviewer, for JavaScript, R and Python:
<https://nvelden.github.io/geneviewer-docs/>.

The library and its schema come from npm (`geneviewer-js`). `scripts/fetch-sources.sh`
reads the R package's man pages and NEWS, and the Python package's sources and
docs, from their public repos.

```sh
npm ci
npm run build     # needs Node, R (base R only) and python3 (standard library only)
npm run preview   # http://127.0.0.1:8484/geneviewer-docs/
npm test          # needs Chrome
```

## Writing for each language

The guide is one text. Where the languages differ, mark it:

- In a sentence: ``[[The `grid` key||`GC_grid()`||`.grid()`]] sets the grid``, with the JavaScript first, R second and Python third. Any can be empty; without the third part, Python reads the R text.
- For whole paragraphs or code: `<div class="lang-r">`, with an empty line after it and before `</div>`. Likewise `lang-js` and `lang-py`.

Links can set the language: `/getting-started?lang=r` or `?lang=py`. `npm test` checks that the R names in the text exist in the R package, and the Python names in the Python package.

## The Python of the guide's charts

Each chart of the guide that shows code has its Python in `python/charts/<id>.py`, written by hand: the R code of the chart in Python. The files run in the order of the guide, after `_setup.py`, so one can use a table an earlier one made. With `geneviewer-py` installed, this checks that each gives the spec recorded from R, that every chart has a file and that no file is left over:

```sh
python scripts/check-python-charts.py
```

The Pages workflow runs it with the Python package at `PY_REF`. When a chart's R code changes, change its Python too.

## After a release

```sh
gh workflow run pages.yml -R nvelden/geneviewer-docs
```

This picks up the newest `geneviewer-js`. For an R release, first set `R_REF`
in `scripts/fetch-sources.sh` to its tag. For a Python release, set `PY_REF`
there and `pyVersion` in `site/.vitepress/config.mjs`.

## When the charts change

The charts are exported from the R package's vignettes and committed. With
`GENEVIEWER_R_DIR` set to a checkout of the R package:

```sh
Rscript scripts/export-examples.R
GENEVIEWER_CHROME=1 npm run gallery
```

## The R articles

An article's source is `articles/<name>.Rmd`. Running it writes its page in
`site/r/articles/` and its charts, both committed, so the code on a page is the
code that ran. It reads its data from a checkout of
[geneviewer-tutorials](https://github.com/nvelden/geneviewer-tutorials):

```sh
GENEVIEWER_R_DIR=... GENEVIEWER_TUTORIALS_DIR=... Rscript scripts/export-articles.R gff
```

Without a name it runs all of them. See the script for what each one needs. A
new article also goes in the sidebar, in `site/.vitepress/config.mjs`.

## The Python pages

The pages under `site/python/` are written by hand. The reference
(`site/python/reference/`) and the pages `naming` and `differences` are made at
build time from the Python package's docstrings and docs
(`scripts/pydoc2md.py`).

A chart on these pages is `@chart python-<name>`: the page shows the chart and
the Python that made it. Both come from `site/public/charts/python-<name>.json`,
written by running the snippets in `scripts/export-python-charts.py` and
committed. With `geneviewer-py[align]` installed and `GENEVIEWER_PY_DIR` set to
a checkout of the Python package:

```sh
python scripts/export-python-charts.py
```

## Licence

MIT. See LICENSE.md.
