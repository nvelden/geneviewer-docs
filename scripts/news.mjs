// The R package's NEWS as a page. v-pre: braces in it are not Vue templates.
import { readFileSync, writeFileSync } from "node:fs";

const news = readFileSync(".sources/geneviewer/NEWS.md", "utf8").replace(/^#\s+geneviewer\s+/gm, "## ");
writeFileSync("site/r/news.md", `# R package changelog\n\n<div v-pre>\n\n${news}\n\n</div>\n`);
