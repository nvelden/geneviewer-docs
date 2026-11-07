// The names the guide uses must exist: for R in the R package (its functions,
// datasets and arguments, from the man pages; npm run sources), for
// JavaScript in the library (the spec schema's options and the names in its
// type definitions). A renamed argument then fails here rather than sending
// readers to a name that is gone.
import { readFileSync, readdirSync } from "node:fs";

const man = ".sources/geneviewer/man";
const known = new Set();
for (const file of readdirSync(man).filter((name) => name.endsWith(".Rd"))) {
  const rd = readFileSync(`${man}/${file}`, "utf8");
  for (const [, name] of rd.matchAll(/\\alias\{([^}]+)\}/g)) known.add(name);
  for (const [, name] of rd.matchAll(/^\\item\{([\w.]+)\}/gm)) known.add(name);
  // Options passed through ... are documented in the text of the argument
  for (const [, name] of rd.matchAll(/\\code\{([A-Za-z][\w.]*)/g)) known.add(name);
}
// Packages, and names that are not arguments: columns of the chart's data and
// the parts of the values Shiny reports
const other = new Set(["webshot2", "rowID", "translation", "sequence", "style", "position", "action", "moves", "moveX", "moveY", "range", "input"]);

const missing = [];
let checked = 0;
const check = (page, text) => {
  for (const [, code] of text.matchAll(/`([^`\n]+)`/g)) {
    if (code.startsWith("input$") || code.startsWith("click$") || code.startsWith("geneviewer:")) continue;
    const name = code.match(/^[A-Za-z][\w.]*/)?.[0];
    if (!name || name === "GC_" || /^(TRUE|FALSE|NULL)$/.test(name)) continue;
    checked += 1;
    if (!known.has(name) && !other.has(name)) missing.push(`${page}: ${code}`);
  }
};

for (const page of ["getting-started", "what-is-geneviewer", "api"]) {
  const source = readFileSync(`site/${page}.md`, "utf8");
  for (const [, , r] of source.matchAll(/\[\[(.*?)\|\|(.*?)\]\]/g)) check(page, r);
  const blocks = source.matchAll(/<div class="lang-r">([\s\S]*?)<\/div>/g);
  for (const [, block] of blocks) check(page, block.replace(/```[\s\S]*?```/g, ""));
}

// JavaScript: every property name of the schema, and every name in the .d.ts
const lib = "node_modules/geneviewer-js/dist";
// The page's D3, and the columns of a links table
const jsKnown = new Set(["geneviewer", "d3", "true", "false", "null", "undefined", "event", "detail", "type",
                         "start1", "end1", "cluster1", "start2", "end2", "cluster2"]);
const collect = (node) => {
  if (Array.isArray(node)) return node.forEach(collect);
  if (!node || typeof node !== "object") return;
  for (const [key, value] of Object.entries(node)) {
    if (key === "properties" || key === "$defs") Object.keys(value).forEach((name) => jsKnown.add(name));
    if (key === "enum") value.forEach((name) => typeof name === "string" && jsKnown.add(name));
    collect(value);
  }
};
collect(JSON.parse(readFileSync(`${lib}/spec-v1.schema.json`, "utf8")));
for (const file of ["geneviewer.d.ts", "spec.d.ts"]) {
  for (const [name] of readFileSync(`${lib}/${file}`, "utf8").matchAll(/[A-Za-z_$][\w$]*/g)) jsKnown.add(name);
}
const jsMissing = [];
let jsChecked = 0;
const checkJs = (page, text) => {
  for (const [, code] of text.matchAll(/`([^`\n]+)`/g)) {
    // R functions are named on purpose, to say what stays in R
    if (code.startsWith("geneviewer:") || code.startsWith("GC_") || /^["'\d<#]/.test(code)) continue;
    const chain = code.match(/^[A-Za-z_$][\w$]*(\.[A-Za-z_$][\w$]*)*/)?.[0];
    if (!chain) continue;
    jsChecked += 1;
    const unknown = chain.split(".").filter((name) => !jsKnown.has(name) && !other.has(name));
    if (unknown.length) jsMissing.push(`${page}: ${code} (${unknown.join(", ")})`);
  }
};
for (const page of ["getting-started", "what-is-geneviewer"]) {
  const source = readFileSync(`site/${page}.md`, "utf8");
  for (const [, js] of source.matchAll(/\[\[(.*?)\|\|(.*?)\]\]/g)) checkJs(page, js);
  for (const [, block] of source.matchAll(/<div class="lang-js">([\s\S]*?)<\/div>/g)) checkJs(page, block.replace(/```[\s\S]*?```/g, ""));
}

if (missing.length) console.error(`R names in the guide that the R package does not have:\n  ${missing.join("\n  ")}`);
if (jsMissing.length) console.error(`JavaScript names in the guide that the library does not have:\n  ${jsMissing.join("\n  ")}`);
if (missing.length || jsMissing.length) process.exit(1);
console.log(`guide names: ${checked} R names found in the R package, ${jsChecked} JavaScript names in the library`);
