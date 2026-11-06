#!/usr/bin/env bash
# What the site reads from the other repos, into .sources/: the schema of the
# geneviewer-js version installed from npm, and the man pages and NEWS of the
# R package. All public, so no token is needed.
set -euo pipefail
cd "$(dirname "$0")/.."

# The R package's docs to show. Set to the release tag at each R release.
R_REF="m6-js-library"

JS_REF="v$(node -p "require('./node_modules/geneviewer-js/package.json').version")"

fetch() { # repo, ref, paths...
  local repo=$1 ref=$2 dir=".sources/$1"
  shift 2
  rm -rf "$dir"
  git clone --quiet --depth 1 --branch "$ref" --filter=blob:none --sparse \
    "https://github.com/nvelden/$repo.git" "$dir"
  git -C "$dir" sparse-checkout set --no-cone "$@"
  echo "$repo at $ref"
}

fetch geneviewer-js "$JS_REF" /schema/
fetch geneviewer "$R_REF" /man/ /NEWS.md
