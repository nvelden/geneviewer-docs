import { readFileSync } from "node:fs";
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vitepress";
import { expand, sections, writeDataFiles } from "./charts.mjs";

const { version } = JSON.parse(readFileSync(new URL("../../node_modules/geneviewer-js/package.json", import.meta.url), "utf8"));
// The R package's version on CRAN, shown in the nav bar. Set at each R release,
// with R_REF in scripts/fetch-sources.sh.
const rVersion = "0.2.0";
// The Python package's version, shown in the nav bar. Set at each Python
// release, with PY_REF in scripts/fetch-sources.sh.
const pyVersion = "0.2.0";
const base = "/geneviewer-docs/";
const dashboard = "https://nvelden.github.io/geneviewer-shinylive/";

// The R reference is made at build time (scripts/rd2md.R)
const rPages = JSON.parse(readFileSync(new URL("./r-reference.json", import.meta.url), "utf8"));
const rItems = (data) => rPages.filter((entry) => entry.data === data)
  .map((entry) => ({ text: entry.page, link: `/r/reference/${entry.page}` }));
const rSidebar = [
  { text: "R package", items: [
    { text: "Installation", link: "/getting-started?lang=r#installation" },
    { text: "Shiny", link: "/getting-started?lang=r#shiny" },
    { text: "Reference", link: "/r/reference/" },
    { text: "Changelog", link: "/r/news" },
    { text: "Gene Cluster Dashboard", link: dashboard },
  ] },
  { text: "Articles", items: [
    { text: "GenBank files", link: "/r/articles/genbank" },
    { text: "GFF files", link: "/r/articles/gff" },
    { text: "FASTA files", link: "/r/articles/fasta" },
    { text: "Protein alignments", link: "/r/articles/protein-alignment" },
    { text: "MUMmer alignments", link: "/r/articles/mummer" },
    { text: "Gene transcripts", link: "/r/articles/transcripts" },
    { text: "A published figure", link: "/r/articles/published-figure" },
  ] },
  { text: "Functions", collapsed: false, items: rItems(false) },
  { text: "Datasets", collapsed: true, items: rItems(true) },
];

// The Python reference is made at build time (scripts/pydoc2md.py)
const pyPages = JSON.parse(readFileSync(new URL("./python-reference.json", import.meta.url), "utf8"));
const pyItems = (data) => pyPages.filter((entry) => entry.data === data)
  .map((entry) => ({ text: entry.title, link: `/python/reference/${entry.page}` }));
// The same sections as the R package's
const pySidebar = [
  { text: "Python package", items: [
    { text: "Installation", link: "/getting-started?lang=py#installation" },
    { text: "Jupyter", link: "/python/jupyter" },
    { text: "Shiny", link: "/python/shiny" },
    { text: "Reference", link: "/python/reference/" },
    { text: "Changelog", link: "/python/news" },
    { text: "Gene Cluster Dashboard", link: dashboard },
  ] },
  { text: "Articles", items: [
    { text: "GenBank files", link: "/python/articles/genbank" },
    { text: "GFF files", link: "/python/articles/gff" },
    { text: "FASTA files", link: "/python/articles/fasta" },
    { text: "Protein alignments", link: "/python/articles/protein-alignment" },
    { text: "MUMmer alignments", link: "/python/articles/mummer" },
    { text: "Gene transcripts", link: "/python/articles/transcripts" },
    { text: "A published figure", link: "/python/articles/published-figure" },
  ] },
  { text: "Functions", collapsed: false, items: pyItems(false) },
  { text: "Datasets", collapsed: true, items: pyItems(true) },
];

const guide = (text, hash) => ({ text, link: `/getting-started#${hash}` });

export default defineConfig({
  title: "geneviewer",
  description: "Interactive gene cluster, transcript and genome alignment charts for JavaScript, R and Python",
  base,
  outDir: "../_site",
  appearance: "force-auto",
  cleanUrls: true,
  sitemap: { hostname: "https://nvelden.github.io/geneviewer-docs/" },
  head: [
    ["link", { rel: "icon", href: `${base}favicon.ico` }],
    // Font Awesome, for the charts with custom toolbar icons: the library draws
    // its own icons itself, and a custom icon by name needs it on the page
    ["link", { rel: "stylesheet", href: "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6/css/all.min.css" }],
    // The language before the page is drawn, so its text does not change on screen.
    // ?lang=r or ?lang=py in a link sets it and is remembered.
    ["script", {}, `(function () {
      var wanted = new URLSearchParams(location.search).get("lang"), saved = null;
      try {
        saved = localStorage.getItem("geneviewer-language");
        if (wanted === "js" || wanted === "r" || wanted === "py") localStorage.setItem("geneviewer-language", wanted);
      } catch (e) {}
      document.documentElement.dataset.lang = wanted === "js" || wanted === "r" || wanted === "py" ? wanted : saved === "r" || saved === "py" ? saved : "js";
    })();`],
  ],
  markdown: {
    config(md) {
      md.core.ruler.before("normalize", "geneviewer-markers", (state) => {
        state.src = expand(state.src);
      });
    },
  },
  vite: {
    resolve: {
      alias: [
        { find: /^.*\/VPFooter\.vue$/, replacement: fileURLToPath(new URL("./theme/SiteFooter.vue", import.meta.url)) },
      ],
    },
    define: { __APP_VERSION__: JSON.stringify(version), __R_VERSION__: JSON.stringify(rVersion), __PY_VERSION__: JSON.stringify(pyVersion) },
  },
  buildEnd(site) {
    writeDataFiles(site.outDir);
  },
  themeConfig: {
    logo: "/logo.png",
    siteTitle: "geneviewer",
    outline: { level: [2, 3], label: "On this page" },
    search: { provider: "local" },
    nav: [
      { text: "Guide", link: "/getting-started", activeMatch: "^/(getting-started|what-is-geneviewer|examples|api)" },
      { text: "R package", link: "/r/reference/", activeMatch: "^/r/" },
      { text: "Python package", link: "/python/reference/", activeMatch: "^/python/" },
      { text: "Dashboard", link: dashboard },
    ],
    sidebar: { "/r/": rSidebar, "/python/": pySidebar, "/": [
      {
        text: "Introduction",
        items: [
          { text: "What is geneviewer?", link: "/what-is-geneviewer" },
          { text: "Getting started", link: "/getting-started" },
          { text: "Examples", link: "/examples" },
          { text: "JavaScript API", link: "/api" },
          { text: "Gene Cluster Dashboard", link: dashboard },
        ],
      },
      {
        text: "Chart parts",
        collapsed: false,
        items: [
          guide("Genes", "genes"),
          guide("Transcripts", "transcripts"),
          guide("Links", "links"),
          guide("Labels", "labels"),
          guide("Annotations", "annotations"),
          guide("Legend", "legend"),
          guide("Scale", "scale"),
          guide("Coordinates", "coordinates"),
          guide("Scale bar", "scale-bar"),
          guide("Tooltip", "tooltip"),
        ],
      },
      {
        text: "Look and feel",
        collapsed: false,
        items: [
          guide("Colors", "colors"),
          guide("Patterns", "patterns"),
          guide("Themes", "themes"),
          guide("Layout", "layout"),
        ],
      },
      {
        text: "Interaction",
        collapsed: false,
        items: [
          guide("Events", "events"),
          guide("Moving elements", "moving-elements"),
          guide("Zoom", "zoom"),
          guide("Toolbar", "toolbar"),
          guide("Saving charts", "saving-charts"),
        ],
      },
      {
        text: "Examples",
        collapsed: true,
        items: sections.map((section) => ({
          text: section.heading.replace(/\*([^*]+)\*/g, "<i>$1</i>").replace(/`([^`]+)`/g, "<code>$1</code>"),
          link: `/examples#${section.id}`,
        })),
      },
    ] },
  },
});
