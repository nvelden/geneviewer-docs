// The charts of the site at build time: the markers in the pages (@chart,
// @examples, @api) become a live chart with its code in tabs. The JavaScript
// is made from the chart's spec, recorded from R (scripts/export-examples.R),
// so what a page shows is what the chart draws.
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { referenceHtml } from "../../scripts/build-reference.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const chartsDir = join(here, "../public/charts");
const SITE = "https://nvelden.github.io/geneviewer-docs";
// R's data frames as a table of rows, inline, up to this many rows
const INLINE_ROWS = 8;
const INLINE_LINK_ROWS = 3;

export const sections = JSON.parse(readFileSync(join(here, "examples.json"), "utf8"))
  .map((section) => ({ ...section, heading: section.heading[0], id: section.id[0] }));

const load = (id) => JSON.parse(readFileSync(join(chartsDir, `${id}.json`), "utf8"));

const columnsToRows = (table) => {
  if (Array.isArray(table)) return table;
  const names = Object.keys(table).filter((name) => name !== "rowID");
  return (table[names[0]] ?? []).map((_, i) => Object.fromEntries(names.map((name) => [name, table[name][i]])));
};
const rowCount = (table) => (table ? columnsToRows(table).length : 0);

// The tables the getting started page introduces once, by name. A table
// counts as the same without the columns R adds to it along the way.
const sameTable = (table) => {
  const names = Object.keys(table).filter((name) => !["rowID", "identity"].includes(name)).sort();
  return JSON.stringify(names.map((name) => [name, table[name]]));
};
const namedTables = new Map([
  ["ophA", "guide-single-gene-cluster"],
  ["ophAClusters", "guide-multiple-gene-clusters"],
  ["dbophA", "guide-coordinates"],
].map(([name, id]) => [sameTable(load(id).spec.data), name]));
// The one chart that colours by the random identity column of its data
const usesGeneIdentity = new Set(["guide-links-3"]);

// JavaScript source of a value: object keys without quotes where they can
// be, short arrays on one line; { $code } is written as code
const identifier = /^[A-Za-z_$][\w$]*$/;
function toJs(value, indent = "") {
  if (value && typeof value === "object" && "$code" in value) return value.$code;
  if (Array.isArray(value)) {
    const flat = `[${value.map((v) => toJs(v, indent)).join(", ")}]`;
    if (flat.length <= 72 && !flat.includes("\n")) return flat;
    const inner = indent + "  ";
    return `[\n${value.map((v) => inner + toJs(v, inner)).join(",\n")},\n${indent}]`;
  }
  if (value && typeof value === "object") {
    const entries = Object.entries(value);
    if (!entries.length) return "{}";
    const inner = indent + "  ";
    const items = entries.map(([key, v]) => {
      if (v && typeof v === "object" && v.$code === key) return `${inner}${key}`;
      return `${inner}${identifier.test(key) ? key : JSON.stringify(key)}: ${toJs(v, inner)}`;
    });
    const flat = `{ ${items.map((item) => item.trim()).join(", ")} }`;
    if (flat.length <= 72 && !flat.includes("\n")) return flat;
    return `{\n${items.join(",\n")},\n${indent}}`;
  }
  return JSON.stringify(value);
}

/** The JavaScript of a chart, and the tables it loads from a data file. */
function javascript(chart) {
  const { id, spec } = chart;
  const { version, height, width, data, ...rest } = spec;
  const tables = {};
  const shown = { version };

  const name = !usesGeneIdentity.has(id) && !Array.isArray(data) ? namedTables.get(sameTable(data)) : null;
  if (name && id.startsWith("guide-")) shown.data = { $code: name };
  else if (rowCount(data) <= INLINE_ROWS) shown.data = columnsToRows(data);
  else {
    tables.data = data;
    shown.data = { $code: "data" };
  }
  Object.assign(shown, rest);

  if (spec.links) {
    const many = Array.isArray(spec.links);
    const entries = (many ? spec.links : [spec.links]).map((entry, i) => {
      if (!entry.data) return entry;
      const { data: linkData, ...options } = entry;
      if (rowCount(linkData) <= INLINE_LINK_ROWS) return { data: columnsToRows(linkData), ...options };
      const tableName = `links${many ? i + 1 : ""}`;
      tables[tableName] = linkData;
      return { data: { $code: tableName }, ...options };
    });
    shown.links = many ? entries : entries[0];
  }

  const names = Object.keys(tables);
  const load = names.length
    ? `const { ${names.join(", ")} } = await fetch("${SITE}/charts/data/${id}.json")\n  .then((response) => response.json());\n\n`
    : "";
  const size = spec.height ?? chart.height;
  return {
    tables,
    code: `// <div id="chart" style="height: ${size}"></div>\n${load}` +
      `const chart = geneviewer.newChart("#chart", ${toJs(shown)});`,
  };
}

const fence = (language, label, code) => {
  const longest = Math.max(2, ...(code.match(/`+/g) ?? []).map((run) => run.length));
  const ticks = "`".repeat(longest + 1);
  return `${ticks}${language} [${label}]\n${code}\n${ticks}`;
};

/** The markdown of one chart. flags: nocode, fold (code in a closed section). */
function chartMarkdown(id, flags = []) {
  const chart = load(id);
  const height = chart.spec.height ?? chart.height;
  const width = chart.width && chart.width !== "100%" ? ` width="${chart.width}"` : "";
  const element = `<GvChart id="${id}" height="${height}"${width}${flags.includes("log") ? " log" : ""} />`;
  if (flags.includes("nocode")) return element;
  const tabs = `::: code-group\n${fence("js", "JavaScript", javascript(chart).code)}\n\n${fence("r", "R", chart.code.trim())}\n:::`;
  if (flags.includes("fold")) {
    return `${element}\n\n<details class="gv-code"><summary>Show the code</summary>\n\n${tabs}\n\n</details>`;
  }
  return `${element}\n\n${tabs}`;
}

// The examples page, section by section as in the R package's Examples page
function examplesMarkdown() {
  return sections.map((section) => {
    const prose = section.prose.join("\n\n")
      .replace(/\]\((?!http)([\w-]+)\.html\)/g, "](https://nvelden.github.io/geneviewer/articles/$1.html)");
    const charts = section.charts.map((id) => chartMarkdown(id, ["fold"])).join("\n\n");
    return `## ${section.heading} {#${section.id}}\n\n${prose}\n\n${charts}`;
  }).join("\n\n");
}

// HTML in markdown must have no blank lines or indents, or it turns to text
// and code blocks; the code in <pre> keeps its lines
function referenceMarkdown() {
  const flat = referenceHtml().split(/(<pre>[\s\S]*?<\/pre>)/).map((part, i) => (i % 2
    ? part.replace(/\n/g, "&#10;")
    : part.replace(/^\s+/gm, "").replace(/\n{2,}/g, "\n"))).join("");
  return `<div v-pre class="gv-reference">\n${flat}\n</div>`;
}

// The named tables, in code, for the getting started page
function tablesMarkdown() {
  const rows = (table) => columnsToRows(table)
    .map((row) => `  ${toJs(row)},`).join("\n");
  const all = load("guide-multiple-gene-clusters").spec.data;
  return "```js\n" +
    `const ophAClusters = [\n${rows(all)}\n];\n` +
    `const ophA = ophAClusters.filter((gene) => gene.cluster === "ophA");\n` +
    `const dbophA = ophAClusters.filter((gene) => gene.cluster === "dbophA");\n` +
    "```";
}

// Text that differs by language, in a sentence: [[JavaScript||R]]. Either can be
// empty, and it can hold Markdown. Run first, so that it works in tables, and
// so that it leaves the code of the charts alone.
function languageText(source) {
  return source.replace(/\[\[(.*?)\|\|(.*?)\]\]/g,
    (_, js, r) => `<span class="lang-js">${js}</span><span class="lang-r">${r}</span>`);
}

/** Replace the markers in a page's source. */
export function expand(source) {
  return languageText(source)
    .replace(/^@chart ([\w-]+)((?: \w+)*)$/gm, (_, id, flags) => chartMarkdown(id, flags.trim().split(" ")))
    .replace(/^@tables$/m, () => tablesMarkdown())
    .replace(/^@examples$/m, () => examplesMarkdown())
    .replace(/^@api$/m, () => referenceMarkdown());
}

/** Write the data files the JavaScript of the charts loads. */
export function writeDataFiles(outDir) {
  const dir = join(outDir, "charts/data");
  mkdirSync(dir, { recursive: true });
  for (const file of readdirSync(chartsDir)) {
    const { tables } = javascript(JSON.parse(readFileSync(join(chartsDir, file), "utf8")));
    if (Object.keys(tables).length) writeFileSync(join(dir, file), JSON.stringify(tables));
  }
}
