# Make the R articles: runs articles/<name>.Rmd and writes the page
# site/r/articles/<name>.md and its charts site/public/charts/article-<name>-<n>.json.
# The code on a page is the code that ran. Any error stops the export.
#
# Needs GENEVIEWER_R_DIR (a checkout of the R package) and
# GENEVIEWER_TUTORIALS_DIR (a checkout of nvelden/geneviewer-tutorials, for the
# data), and for some articles MUMmer, Biostrings and pwalign. Run from the repo
# root:
#   Rscript scripts/export-articles.R            # all
#   Rscript scripts/export-articles.R gff fasta  # some

names <- commandArgs(trailingOnly = TRUE)
if (!length(names)) names <- sub("\\.Rmd$", "", list.files("articles", "\\.Rmd$"))

# Each in its own R: the packages one article attaches must not change another
if (length(names) > 1) {
  script <- sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE))
  for (name in names) {
    if (system2(file.path(R.home("bin"), "Rscript"), c(shQuote(script), name)) != 0) stop(name, " failed.")
  }
  quit(save = "no")
}

for (dir in c("GENEVIEWER_R_DIR", "GENEVIEWER_TUTORIALS_DIR")) {
  if (!dir.exists(Sys.getenv(dir))) stop("Set ", dir, ".")
}
suppressMessages(pkgload::load_all(Sys.getenv("GENEVIEWER_R_DIR"), quiet = TRUE))
suppressMessages(library(dplyr))
library(magrittr)
options(geneviewer.record_spec = TRUE)
out_dir <- "site/public/charts"
source("scripts/write-chart.R")

name <- names
lines <- readLines(file.path("articles", paste0(name, ".Rmd")), warn = FALSE)
header <- which(lines == "---")[1:2]
title <- sub('^title: "(.*)"$', "\\1", lines[header[1] + 1])
lines <- lines[(header[2] + 1):length(lines)]

unlink(Sys.glob(file.path(out_dir, paste0("article-", name, "-*.json"))))

# A table as Markdown; < and {{ in its values are text, not HTML or Vue
table_lines <- function(table) {
  gsub("{{", "&#123;&#123;", gsub("<", "&lt;", as.character(table), fixed = TRUE), fixed = TRUE)
}

env <- new.env(parent = globalenv())
set.seed(1)
page <- c(
  paste0("<!-- Made by scripts/export-articles.R from articles/", name, ".Rmd. Edit that. -->"),
  "",
  paste("#", title)
)
charts <- 0
fenced <- FALSE
i <- 1
while (i <= length(lines)) {
  line <- lines[i]
  if (!fenced && grepl("^```\\{r", line)) {
    end <- i + which(trimws(lines[(i + 1):length(lines)]) == "```")[1]
    code <- lines[seq_len(end - i - 1) + i]
    while (length(code) && !nzchar(trimws(code[length(code)]))) code <- code[-length(code)]
    while (length(code) && !nzchar(trimws(code[1]))) code <- code[-1]
    code <- paste(code, collapse = "\n")
    settings <- sub("^```\\{r,?\\s*(.*)\\}\\s*$", "\\1", line)
    settings <- eval(parse(text = paste0("list(", settings, ")")))
    option <- function(key, default) if (is.null(settings[[key]])) default else settings[[key]]
    show <- option("include", TRUE)
    if (show && option("echo", TRUE)) page <- c(page, "", "```r", code, "```")
    if (option("eval", TRUE)) {
      for (expression in parse(text = code, keep.source = FALSE)) {
        result <- suppressMessages(suppressWarnings(withVisible(eval(expression, env))))
        if (!result$visible || !show || identical(option("results", "markup"), "hide")) next
        if (inherits(result$value, "knitr_kable")) {
          page <- c(page, "", table_lines(result$value))
        } else if (inherits(result$value, "htmlwidget")) {
          charts <- charts + 1
          id <- write_chart(result$value, paste0("article-", name, "-", charts), code)
          page <- c(page, "", paste("@chart", id, "nocode"))
        }
      }
    }
    i <- end + 1
    next
  }
  if (grepl("^```", line)) fenced <- !fenced
  if (!fenced && grepl("^### ", line)) line <- sub("^###", "##", line)
  # The title is the introduction's heading
  if (!(line == "## Intro")) page <- c(page, trimws(line, "right"))
  i <- i + 1
}
page <- gsub("\n{3,}", "\n\n", paste(page, collapse = "\n"))
dir.create("site/r/articles", showWarnings = FALSE, recursive = TRUE)
writeLines(paste0(trimws(page), ""), file.path("site/r/articles", paste0(name, ".md")), useBytes = TRUE)
cat(name, ":", charts, "charts\n")
