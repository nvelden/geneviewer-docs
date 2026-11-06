// Make the thumbnails of the home page's gallery from the charts of the site:
// site/public/gallery/<id>.jpg and the list site/.vitepress/gallery.json. The
// images are committed, as the site's build has no browser. Run after
// scripts/export-examples.R when the charts change: npm run site:gallery
// (needs a Playwright browser, or Chrome with GENEVIEWER_CHROME=1).
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { chromium } from "playwright-core";

const SIDE = 320; // pixels of a thumbnail

// [chart, title, link on the site]
const items = [
  ["e-coli-lac-operon", "E. coli lac operon", "/examples#e-coli-lac-operon"],
  ["omphalotin-gene-clusters", "Omphalotin gene clusters", "/examples#omphalotin-gene-clusters"],
  ["omphalotin-gene-clusters-2", "Omphalotin gene clusters", "/examples#omphalotin-gene-clusters"],
  ["omphalotin-gene-clusters-3", "Omphalotin gene clusters", "/examples#omphalotin-gene-clusters"],
  ["h-sapiens-hox-genes-using-biomart", "H. sapiens Hox genes", "/examples#h-sapiens-hox-genes-using-biomart"],
  ["brca1-splice-variants", "BRCA1 splice variants", "/examples#brca1-splice-variants"],
  ["saccharopolyspora-erythraea-erythromycin", "Erythromycin gene clusters", "/examples#saccharopolyspora-erythraea-erythromycin"],
  ["saccharopolyspora-erythraea-erythromycin-protein-alignment", "Erythromycin protein alignment", "/examples#saccharopolyspora-erythraea-erythromycin-protein-alignment"],
  ["saccharopolyspora-erythraea-erythromycin-protein-alignment-2", "Erythromycin protein alignment", "/examples#saccharopolyspora-erythraea-erythromycin-protein-alignment"],
  ["blakpc-2-plasmid-pqeb1-and-its-variants", "blaKPC-2 plasmid pQEB1", "/examples#blakpc-2-plasmid-pqeb1-and-its-variants"],
  ["tn7-like-transposons-carrying-a-crispr-cas-system", "Tn7-like transposons", "/examples#tn7-like-transposons-carrying-a-crispr-cas-system"],
  ["genomes-of-the-four-coronavirus-genera", "Coronavirus genomes", "/examples#genomes-of-the-four-coronavirus-genera"],
  ["mitochondrial-gene-order-locust-and-human", "Mitochondrial gene order", "/examples#mitochondrial-gene-order-locust-and-human"],
  ["guide-themes", "The dark theme", "/getting-started#themes"],
  ["guide-themes-2", "The vintage theme", "/getting-started#themes"],
  ["guide-themes-4", "The black and white theme", "/getting-started#themes"],
  ["guide-patterns-2", "Patterns", "/getting-started#patterns"],
  ["guide-links-3", "Links by identity", "/getting-started#links"],
  ["guide-transcripts-2", "Transcripts", "/getting-started#transcripts"],
  ["guide-prevent-gene-overlap-2", "Nested genes", "/getting-started#prevent-gene-overlap"],
  ["guide-spread-labels", "Spread labels", "/getting-started#spread-labels"],
  ["guide-labels", "Labels", "/getting-started#labels"],
];

const outDir = "site/public/gallery";
rmSync(outDir, { recursive: true, force: true });
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch(process.env.GENEVIEWER_CHROME ? { channel: "chrome" } : {});
const gallery = [];
for (const [id, title, link] of items) {
  const { spec, height } = JSON.parse(readFileSync(`site/public/charts/${id}.json`, "utf8"));
  const h = parseInt(spec.height ?? height, 10);
  const w = Math.max(Math.round(h * 1.6), 360);
  const side = Math.min(h, w);
  const page = await browser.newPage({
    viewport: { width: w, height: h },
    deviceScaleFactor: SIDE / side,
  });
  await page.setContent(`<!DOCTYPE html><html><body style="margin:0;background:#fff"><div id="chart" style="width:${w}px;height:${h}px"></div></body></html>`);
  await page.addScriptTag({ path: "node_modules/geneviewer-js/dist/geneviewer.min.js" });
  // A small tile shows the genes: titles and legends would be cut off
  const { title: _title, clusterFooter: _footer, ...shown } = spec;
  const legend = Array.isArray(shown.legend) ? shown.legend[0] : shown.legend;
  await page.evaluate((chartSpec) => {
    geneviewer.newChart("#chart", chartSpec);
  }, { ...shown, legend: { ...legend, show: false } });
  await page.waitForTimeout(400);
  const image = `/gallery/${id}.jpg`;
  await page.screenshot({
    path: `site/public${image}`,
    type: "jpeg",
    quality: 78,
    clip: { x: (w - side) / 2, y: (h - side) / 2, width: side, height: side },
  });
  await page.close();
  gallery.push({ title, image, link });
}
await browser.close();
writeFileSync("site/.vitepress/gallery.json", `${JSON.stringify(gallery, null, 2)}\n`);
console.log(`wrote ${gallery.length} thumbnails`);
