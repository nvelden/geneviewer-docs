// The names the guide uses for R must exist in the R package: its functions,
// datasets and arguments, from the man pages (npm run sources). A renamed
// argument then fails here rather than sending readers to a name that is gone.
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

if (missing.length) {
  console.error(`R names in the guide that the R package does not have:\n  ${missing.join("\n  ")}`);
  process.exit(1);
}
console.log(`guide names: ${checked} R names found in the R package`);
