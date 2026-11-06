# The R reference of the docs site: Rd files to Markdown. Base R only.
# Usage: Rscript rd2md.R <man dir> <out dir> <index json>
#
# Fails if a page would lose content: an Rd tag it does not know, or a word that
# R's own text rendering of the page has and the Markdown does not.
args <- commandArgs(TRUE); man <- args[[1]]; out <- args[[2]]; manifest <- args[[3]]
dir.create(out, recursive = TRUE, showWarnings = FALSE)
unknown <- new.env()
tag <- function(x) { t <- attr(x, "Rd_tag"); if (is.null(t)) "" else t }
files <- list.files(man, "\\.Rd$", full.names = TRUE)

# Which page documents each topic, so that \link{} finds it
parsed <- lapply(files, tools::parse_Rd)
names(parsed) <- sub("\\.Rd$", "", basename(files))
topics <- list()
for (page in names(parsed)) for (x in parsed[[page]]) {
  if (tag(x) %in% c("\\alias", "\\name")) topics[[paste(unlist(x), collapse = "")]] <- page
}

esc <- function(s) {
  s <- gsub("\\", "\\\\", s, fixed = TRUE)
  s <- gsub("<", "&lt;", s, fixed = TRUE)
  s <- gsub("{{", "&#123;&#123;", s, fixed = TRUE)
  s <- gsub("|", "\\|", s, fixed = TRUE)
  gsub("([*_`\\[])", "\\\\\\1", s)
}
raw <- function(x) if (is.list(x)) paste(vapply(x, raw, ""), collapse = "") else paste(as.character(x), collapse = "")
code_text <- function(x) {
  if (is.list(x)) {
    t <- tag(x)
    if (t %in% c("\\dots", "\\ldots")) return("...")
    if (t %in% c("\\link", "\\code", "\\dQuote", "\\sQuote", "\\emph")) return(paste(vapply(x, code_text, ""), collapse = ""))
    return(paste(vapply(x, code_text, ""), collapse = ""))
  }
  t <- tag(x)
  if (t == "COMMENT") return("")
  as.character(x)
}
inline_code <- function(s) {
  s <- trimws(s)
  ticks <- if (grepl("`", s, fixed = TRUE)) "``" else "`"
  # a pipe would end the cell of a table
  paste0(ticks, s, ticks)
}
link_md <- function(x) {
  text <- code_text(x)
  opt <- attr(x, "Rd_option")
  target <- if (!is.null(opt)) raw(opt) else text
  target <- sub("\\(\\)$", "", sub("^[^:]*:", "", target))
  key <- sub("\\(\\)$", "", text)
  page <- topics[[key]]; if (is.null(page)) page <- topics[[target]]
  label <- inline_code(text)
  if (is.null(page)) return(label)
  sprintf("[%s](./%s)", label, page)
}
items <- function(x, marker) {
  # \item splits a list of siblings
  out <- character(); cur <- NULL; i <- 0
  for (el in x) {
    if (tag(el) == "\\item") {
      if (!is.null(cur)) out <- c(out, cur)
      i <- i + 1; cur <- if (marker == "1.") paste0(i, ". ") else "- "
      if (length(el) == 2) cur <- paste0(cur, "**", trimws(md(el[[1]])), "**: ", trimws(md(el[[2]])))
    } else if (!is.null(cur)) cur <- paste0(cur, md_one(el))
  }
  if (!is.null(cur)) out <- c(out, cur)
  out <- gsub("\n[ \t]*", " ", trimws(out))
  paste0("\n\n", paste(out, collapse = "\n"), "\n\n")
}
md_one <- function(x) {
  t <- tag(x)
  switch(t,
    TEXT = esc(as.character(x)), RCODE = as.character(x), VERB = as.character(x), COMMENT = "",
    "\\code" = , "\\samp" = , "\\file" = , "\\env" = , "\\option" = , "\\command" = , "\\kbd" = , "\\var" = {
      if (length(x) == 1 && tag(x[[1]]) == "\\link") link_md(x[[1]]) else inline_code(code_text(x))
    },
    "\\link" = link_md(x), "\\linkS4class" = inline_code(code_text(x)),
    "\\emph" = paste0("*", md(x), "*"), "\\strong" = , "\\bold" = paste0("**", md(x), "**"),
    "\\pkg" = paste0("**", md(x), "**"), "\\dfn" = , "\\cite" = paste0("*", md(x), "*"),
    "\\dQuote" = paste0("“", md(x), "”"), "\\sQuote" = paste0("‘", md(x), "’"),
    "\\url" = sprintf("<%s>", raw(x)),
    "\\href" = sprintf("[%s](%s)", md(x[[2]]), raw(x[[1]])),
    "\\dots" = , "\\ldots" = "...", "\\R" = "R", "\\cr" = "  \n", "\\tab" = " | ",
    "\\eqn" = , "\\deqn" = inline_code(raw(x[[length(x)]])),
    "\\itemize" = items(x, "-"), "\\enumerate" = items(x, "1."), "\\describe" = items(x, "-"),
    "\\preformatted" = paste0("\n\n```\n", trimws(code_text(x)), "\n```\n\n"),
    "\\if" = , "\\ifelse" = {
      if (raw(x[[1]]) %in% c("html", "TRUE")) md(x[[2]]) else if (t == "\\ifelse") md(x[[3]]) else ""
    },
    "\\out" = raw(x), "\\figure" = "", "\\special" = md(x), "\\enc" = md(x[[1]]), "\\acronym" = md(x),
    "\\subsection" = paste0("\n\n### ", trimws(md(x[[1]])), "\n\n", md(x[[2]]), "\n\n"),
    "\\tabular" = {
      cells <- trimws(strsplit(md(x[[2]]), "  \n", fixed = TRUE)[[1]])
      cells <- cells[nzchar(cells)]
      n <- nchar(gsub("[^lrc]", "", raw(x[[1]])))
      paste0("\n\n", cells[1], "\n", paste(rep("---", n), collapse = " | "), "\n",
             paste(cells[-1], collapse = "\n"), "\n\n")
    },
    "\\verb" = inline_code(raw(x)),
    "\\Sexpr" = {
      m <- regmatches(raw(x), regexec('Rd_expr_doi\\("(.*)"\\)', raw(x)))[[1]]
      if (length(m) == 2) sprintf("[doi:%s](https://doi.org/%s)", m[2], m[2]) else {
        assign("\\Sexpr", TRUE, envir = unknown); ""
      }
    },
    USERMACRO = "",
    {
      assign(t, TRUE, envir = unknown)
      if (is.list(x)) paste(vapply(x, md_one, ""), collapse = "") else esc(as.character(x))
    }
  )
}
md <- function(x) if (is.list(x) && tag(x) != "\\link") paste(vapply(x, md_one, ""), collapse = "") else md_one(x)
section <- function(rd, name) Filter(function(x) tag(x) == name, rd)
examples_text <- function(x) {
  walk <- function(el) {
    t <- tag(el)
    if (t %in% c("\\dontshow", "\\testonly")) return("")
    if (t == "\\donttest") return(paste(vapply(el, walk, ""), collapse = ""))
    if (t == "\\dontrun") {
      return(paste0("## Not run:", paste(vapply(el, walk, ""), collapse = ""), "## End(Not run)"))
    }
    if (is.list(el)) return(code_text(el))
    as.character(el)
  }
  trimws(paste(vapply(x, walk, ""), collapse = ""))
}
for (page in names(parsed)) {
  rd <- parsed[[page]]
  one <- function(n) { s <- section(rd, n); if (length(s)) s[[1]] else NULL }
  lines <- paste0("# ", trimws(gsub("\n", " ", md(one("\\title")))), "\n")
  if (!is.null(s <- one("\\description"))) lines <- c(lines, trimws(md(s)), "")
  if (!is.null(s <- one("\\usage"))) lines <- c(lines, "## Usage\n", "```r", trimws(code_text(s)), "```", "")
  if (!is.null(s <- one("\\arguments"))) {
    lines <- c(lines, "## Arguments\n", "| Argument | Description |", "| --- | --- |")
    for (it in s) if (tag(it) == "\\item") {
      d <- trimws(md(it[[2]])); d <- gsub("\n\n+- ", "<br>- ", d); d <- gsub("\n+", " ", d)
      d <- gsub("(?<!\\\\)\\|", "\\\\|", d, perl = TRUE)
      lines <- c(lines, sprintf("| %s | %s |", inline_code(code_text(it[[1]])), d))
    }
    lines <- c(lines, "")
  }
  if (!is.null(s <- one("\\value"))) lines <- c(lines, "## Value\n", trimws(md(s)), "")
  if (!is.null(s <- one("\\format"))) lines <- c(lines, "## Format\n", trimws(md(s)), "")
  if (!is.null(s <- one("\\source"))) lines <- c(lines, "## Source\n", trimws(md(s)), "")
  if (!is.null(s <- one("\\details"))) lines <- c(lines, "## Details\n", trimws(md(s)), "")
  for (s in section(rd, "\\section")) lines <- c(lines, paste0("## ", trimws(md(s[[1]])), "\n"), trimws(md(s[[2]])), "")
  if (!is.null(s <- one("\\note"))) lines <- c(lines, "## Note\n", trimws(md(s)), "")
  if (!is.null(s <- one("\\references"))) lines <- c(lines, "## References\n", trimws(md(s)), "")
  if (!is.null(s <- one("\\seealso"))) lines <- c(lines, "## See also\n", trimws(md(s)), "")
  if (!is.null(s <- one("\\examples"))) lines <- c(lines, "## Examples\n", "```r", examples_text(s), "```", "")
  writeLines(lines, file.path(out, paste0(page, ".md")), useBytes = TRUE)
}

# The index: functions and datasets, for the page and the sidebar
entries <- lapply(names(parsed), function(page) {
  rd <- parsed[[page]]
  title <- trimws(gsub("\\s+", " ", md(section(rd, "\\title")[[1]])))
  type <- section(rd, "\\docType")
  list(page = page, title = title, data = length(type) > 0 && trimws(raw(type[[1]])) == "data")
})
json_string <- function(s) paste0('"', gsub('"', '\\"', gsub("\\", "\\\\", s, fixed = TRUE), fixed = TRUE), '"')
writeLines(paste0("[\n", paste(vapply(entries, function(e) sprintf(
  '{"page": %s, "data": %s}', json_string(e$page), tolower(e$data)), ""), collapse = ",\n"), "\n]"), manifest)
table_of <- function(items) c("| | |", "| --- | --- |", vapply(items, function(e) sprintf(
  "| [`%s`](./%s) | %s |", e$page, e$page, gsub("|", "\\|", e$title, fixed = TRUE)), ""))
is_data <- vapply(entries, function(e) e$data, TRUE)
writeLines(c("---", "prev: false", "next: false", "---", "", "# R reference", "",
             "Every function and dataset of the R package.", "",
             "## Functions", "", table_of(entries[!is_data]), "",
             "## Datasets", "", table_of(entries[is_data])), file.path(out, "index.md"))

# Nothing may get lost: compare with R's own text rendering of each page
words <- function(s) {
  w <- strsplit(trimws(gsub("[^[:alnum:]_.]+", " ", tolower(paste(s, collapse = " ")))), " +")[[1]]
  gsub("^[._]+|[._]+$", "", w)
}
# Section names, and how R's text output prints the \doi macro
ignore <- c("description", "arguments", "details", "value", "usage", "examples", "note", "references",
            "format", "source", "see", "also", "", "sexpr", "results", "rd", "tools", "rd_expr_doi")
lost <- list()
for (f in files) {
  page <- sub("\\.Rd$", "", basename(f))
  tmp <- tempfile()
  suppressWarnings(tools::Rd2txt(f, out = tmp, options = list(underline_titles = FALSE)))
  page_md <- readLines(file.path(out, paste0(page, ".md")), warn = FALSE)
  page_md <- gsub("\\_", "_", gsub("&lt;", "<", page_md, fixed = TRUE), fixed = TRUE)
  # As counts: a dropped sentence often has words that are elsewhere on the page
  rendered <- table(words(readLines(tmp, warn = FALSE)))
  on_page <- table(words(page_md))
  found <- as.integer(on_page[names(rendered)])
  found[is.na(found)] <- 0L
  missing <- setdiff(names(rendered)[as.integer(rendered) > found], ignore)
  if (length(missing)) lost[[page]] <- missing
}

problems <- character()
if (length(ls(unknown, all.names = TRUE))) {
  problems <- c(problems, paste("Unknown Rd tags:", paste(ls(unknown, all.names = TRUE), collapse = ", ")))
}
for (page in names(lost)) problems <- c(problems, paste0(page, " lost: ", paste(lost[[page]], collapse = ", ")))
if (length(problems)) {
  writeLines(problems, stderr())
  quit(status = 1)
}
cat("R reference:", length(parsed), "pages\n")
