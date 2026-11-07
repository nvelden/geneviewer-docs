#!/usr/bin/env bash
# What the site reads from another repo, into .sources/: the man pages and NEWS
# of the R package. Public, so no token is needed.
set -euo pipefail
cd "$(dirname "$0")/.."

# The R package's docs to show. Set to the release tag at each R release, and
# rVersion in site/.vitepress/config.mjs to its version.
R_REF="m6-js-library"

fetch() { # repo, ref, paths...
  local repo=$1 ref=$2 dir=".sources/$1"
  shift 2
  rm -rf "$dir"
  git clone --quiet --depth 1 --branch "$ref" --filter=blob:none --sparse \
    "https://github.com/nvelden/$repo.git" "$dir"
  git -C "$dir" sparse-checkout set --no-cone "$@"
  echo "$repo at $ref"
}

fetch geneviewer "$R_REF" /man/ /NEWS.md
