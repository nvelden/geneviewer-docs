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

## The Python of the charts

Each chart of the guide, the examples and "What is geneviewer?" that shows code has its Python in `python/charts/<id>.py`, written by hand: the R code of the chart in Python. The files of the guide run in its order, after `_setup.py`, so one can use a table an earlier one made; the others run on their own. With `geneviewer-py` installed, this checks that each gives the spec recorded from R, that every chart has a file and that no file is left over:

```sh
python scripts/check-python-charts.py
```

The Pages workflow runs it with the Python package at `PY_REF`. When a chart's R code changes, change its Python too.

## The Python pages

The Python package has the sections of the R package: a reference, a changelog and the same articles.

- The reference (`site/python/reference/`) and the changelog (`site/python/news.md`) are made at build time (`scripts/pydoc2md.py`): a page per function and method from the docstrings, a page per dataset from the R reference's page of that dataset, and the changelog from the package's `NEWS.md`.
- An article's source is `articles/python/<name>.md`, the R article of that name in Python. Running it writes its page in `site/python/articles/`, committed, so the code on a page is the code that ran. A chart that is the same as the R article's is shown from the R article's file. See the script for the kinds of code block:

  ```sh
  GENEVIEWER_TUTORIALS_DIR=... python scripts/export-python-articles.py gff
  ```

  When an R article changes, change its Python article too.
- `site/python/index.md` and `site/python/shiny.md` are written by hand. A chart on them is `@chart python-<name>`: the page shows the chart and the Python that made it, both from `site/public/charts/python-<name>.json`, written by `python scripts/export-python-charts.py` and committed.

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

## Licence

MIT. See LICENSE.md.
