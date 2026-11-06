# geneviewer-docs

The documentation site of geneviewer, for JavaScript, R and, later, Python:
<https://nvelden.github.io/geneviewer-docs/>.

The library comes from npm (`geneviewer-js`). `scripts/fetch-sources.sh` reads
its schema and the R package's man pages and NEWS from their public repos.

```sh
npm ci
npm run build     # needs Node and R (base R only)
npm run preview   # http://127.0.0.1:8484/geneviewer-docs/
npm test          # needs Chrome
```

## After a release

```sh
gh workflow run pages.yml -R nvelden/geneviewer-docs
```

This picks up the newest `geneviewer-js`. For an R release, first set `R_REF`
in `scripts/fetch-sources.sh` to its tag.

## When the charts change

The charts are exported from the R package's vignettes and committed. With
`GENEVIEWER_R_DIR` set to a checkout of the R package:

```sh
Rscript scripts/export-examples.R
GENEVIEWER_CHROME=1 npm run gallery
```

## Licence

MIT. See LICENSE.md.
