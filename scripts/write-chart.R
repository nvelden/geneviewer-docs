# Write a chart to <out_dir>/<id>.json: its R code, height and the chart spec R
# records (options(geneviewer.record_spec = TRUE)). Gives its id.
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
