# Export the charts of the documentation site from the geneviewer R package.
#
# Runs the two vignettes the site follows, vignettes/Examples.Rmd and
# vignettes/geneviewer.Rmd, and writes for each chart they draw
# site/public/charts/<id>.json: its R code, height and the chart spec R
# records (options(geneviewer.record_spec = TRUE)). The examples page is
# listed in site/.vitepress/examples.json, by section of the vignette. The site
# draws the charts from the specs with the JavaScript in this repo and shows
# each chart's JavaScript, made from its spec (site/.vitepress/charts.mjs).
#
# Run from the repo root, with GENEVIEWER_R_DIR set (or in .try-app.env):
#   Rscript scripts/export-examples.R

env_file <- ".try-app.env"
if (file.exists(env_file) && !nzchar(Sys.getenv("GENEVIEWER_R_DIR"))) {
  readRenviron(env_file)
}
r_dir <- gsub('^"|"$', "", Sys.getenv("GENEVIEWER_R_DIR"))
if (!dir.exists(r_dir)) stop("Set GENEVIEWER_R_DIR to the geneviewer R package repo.")

suppressMessages(pkgload::load_all(r_dir, quiet = TRUE))
suppressMessages(library(dplyr))
library(magrittr)
options(geneviewer.record_spec = TRUE)

out_dir <- "site/public/charts"
unlink(out_dir, recursive = TRUE)
dir.create(out_dir, recursive = TRUE)

slug <- function(text) {
  text <- gsub("[*`]", "", text)
  text <- gsub("[^a-z0-9]+", "-", tolower(text))
  gsub("^-|-$", "", text)
}

# The headings, prose and code chunks of an R Markdown file, in order
parse_rmd <- function(path) {
  lines <- readLines(path, warn = FALSE)
  lines <- lines[(which(lines == "---")[2] + 1):length(lines)]
  blocks <- list()
  i <- 1
  while (i <= length(lines)) {
    line <- lines[i]
    if (grepl("^```\\{r", line)) {
      end <- i + which(lines[(i + 1):length(lines)] == "```")[1]
      options <- sub("^```\\{r,?\\s*(.*)\\}$", "\\1", line)
      blocks[[length(blocks) + 1]] <- list(
        type = "chunk",
        code = paste(lines[seq_len(end - i - 1) + i], collapse = "\n"),
        echo = !grepl("echo\\s*=\\s*FALSE", options),
        eval = !grepl("eval\\s*=\\s*FALSE", options),
        hidden = grepl("results\\s*=\\s*['\"]hide['\"]", options),
        include = !grepl("include\\s*=\\s*FALSE", options)
      )
      i <- end + 1
      next
    }
    if (grepl("^#{2,3} ", line)) {
      text <- sub("\\s*\\{#[^}]*\\}\\s*$", "", sub("^#+ ", "", line))
      blocks[[length(blocks) + 1]] <- list(type = "heading", text = text)
    } else if (nzchar(trimws(line)) && !grepl("^</?(details|summary|br)", line)) {
      blocks[[length(blocks) + 1]] <- list(type = "prose", text = line)
    }
    i <- i + 1
  }
  blocks
}

# Write the chart, gives its id
write_chart <- function(widget, id, code, title = NULL) {
  sent <- htmlwidgets:::createPayload(widget)
  if (length(sent$evals)) {
    stop(id, ": JavaScript functions in the payload are not supported.")
  }
  height <- widget$height
  if (is.numeric(height)) height <- paste0(height, "px")
  width <- widget$width
  if (is.numeric(width)) width <- paste0(width, "px")
  meta <- list(
    id = id,
    code = code,
    height = if (is.null(height)) "400px" else height
  )
  if (!is.null(width)) meta$width <- width
  if (!is.null(title)) meta$title <- title
  # The spec is serialised on its own so htmlwidgets' JSON settings apply
  json <- as.character(jsonlite::toJSON(meta, auto_unbox = TRUE))
  json <- paste0(substr(json, 1, nchar(json) - 1), ',"spec":', htmlwidgets:::toJSON(sent$x$spec), "}")
  writeLines(json, file.path(out_dir, paste0(id, ".json")), useBytes = TRUE)
  id
}

# Run a vignette in one environment and write its charts. A chart's R code
# is its own chunk when that is shown, else the chunks shown before it that
# nothing has claimed yet (the vignettes show the code in a chunk that is
# not run, or run with results = 'hide', above the chunk that draws).
export_vignette <- function(path, prefix = "") {
  env <- new.env(parent = globalenv())
  # Column values drawn at random in the vignettes stay the same between runs
  set.seed(1)
  sections <- list()
  section <- NULL
  pending <- character()
  counts <- list()
  flush <- function() if (!is.null(section)) sections[[length(sections) + 1]] <<- section
  for (block in parse_rmd(path)) {
    if (block$type == "heading") {
      flush()
      section <- list(heading = block$text, id = slug(block$text), prose = character(), charts = character())
      pending <- character()
      next
    }
    if (is.null(section)) {
      section <- list(heading = "", id = "top", prose = character(), charts = character())
    }
    if (block$type == "prose") {
      section$prose <- c(section$prose, block$text)
      next
    }
    if (block$eval) {
      expressions <- parse(text = block$code, keep.source = FALSE)
      for (expression in expressions) {
        result <- tryCatch(
          suppressMessages(suppressWarnings(withVisible(eval(expression, env)))),
          error = function(e) {
            message("FAILED in '", section$heading, "': ", conditionMessage(e))
            list(visible = FALSE, value = NULL)
          }
        )
        if (result$visible && inherits(result$value, "htmlwidget") && block$include && !block$hidden) {
          code <- if (block$echo || !length(pending)) block$code else paste(pending, collapse = "\n\n")
          if (!block$echo) pending <- character()
          n <- (if (is.null(counts[[section$id]])) 0 else counts[[section$id]]) + 1
          counts[[section$id]] <- n
          id <- paste0(prefix, section$id, if (n > 1) paste0("-", n))
          section$charts <- c(section$charts, write_chart(result$value, id, code))
        }
      }
    }
    # Shown, but what it draws (if anything) is drawn by a later chunk
    if (block$echo && block$include && (!block$eval || block$hidden)) {
      pending <- c(pending, block$code)
    }
  }
  flush()
  sections
}

vignettes <- file.path(r_dir, "vignettes")

# The examples page follows Examples.Rmd section by section
examples <- export_vignette(file.path(vignettes, "Examples.Rmd"))
examples <- Filter(function(s) length(s$charts) > 0, examples)
writeLines(
  jsonlite::toJSON(examples, auto_unbox = FALSE, pretty = TRUE),
  "site/.vitepress/examples.json"
)
cat(length(examples), "example sections,", sum(lengths(lapply(examples, `[[`, "charts"))), "charts\n")

# The getting started page picks charts of geneviewer.Rmd by id
guide <- export_vignette(file.path(vignettes, "geneviewer.Rmd"), prefix = "guide-")
cat(sum(lengths(lapply(guide, `[[`, "charts"))), "getting started charts\n")

# The chart whose events the "What is geneviewer?" page shows
interactive <- GC_chart(ophA_clusters, group = "class", cluster = "cluster", height = "320px") %>%
  GC_labels("name") %>%
  GC_links("class", measure = "identity") %>%
  GC_clusterLabel() %>%
  GC_zoom() %>%
  GC_events(select = TRUE)
write_chart(interactive, "interactive", 'GC_chart(ophA_clusters, group = "class", cluster = "cluster",
         height = "320px") %>%
  GC_labels("name") %>%
  GC_links("class", measure = "identity") %>%
  GC_clusterLabel() %>%
  GC_zoom() %>%
  GC_events(select = TRUE)')
