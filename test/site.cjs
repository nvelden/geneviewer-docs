// Site check: serves _site/ (npm run site) and loads its pages. Every chart
// draws, nothing shows an error, the console has no errors, the event log
// of the interactive chart logs a selection, the JavaScript shown with each
// chart runs and draws the same chart, each example has JavaScript and R code,
// the examples follow the R package's, and the API reference lists every
// option of the schema. Run through `npm test`.
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const { chromium } = require("playwright-core");

const root = path.join(__dirname, "..", "_site");
const types = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css",
                ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png" };

(async () => {
  if (!fs.existsSync(path.join(root, "index.html"))) throw new Error("_site/ is missing: run npm run site.");
  // As on GitHub Pages: under /geneviewer-docs/, and /name serves name.html
  const server = http.createServer((req, res) => {
    const url = decodeURIComponent(new URL(req.url, "http://localhost").pathname).replace(/^\/geneviewer-docs/, "");
    let file = path.join(root, url.endsWith("/") ? url + "index.html" : url);
    if (!fs.existsSync(file) && fs.existsSync(`${file}.html`)) file = `${file}.html`;
    if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404).end();
      return;
    }
    res.writeHead(200, { "Content-Type": types[path.extname(file)] || "application/octet-stream" });
    fs.createReadStream(file).pipe(res);
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const base = `${origin}/geneviewer-docs/`;
  const browser = await chromium.launch({
    args: ["--font-render-hinting=none", "--disable-gpu"],
    ...(process.env.GENEVIEWER_CHROME ? { channel: "chrome" } : {}),
  });
  const failures = [];
  const expect = (ok, message) => {
    console.log(`${ok ? "pass" : "FAIL"}  ${message}`);
    if (!ok) failures.push(message);
  };
  try {
    const library = fs.readFileSync(path.join(__dirname, "..", "node_modules", "geneviewer-js", "dist", "geneviewer.min.js"), "utf8");

    // A blank page with the library, whose requests to the published site
    // are answered from _site/: the code runs as a reader's page would run it
    const blankPage = async (setup) => {
      const page = await browser.newPage({ viewport: { width: 900, height: 700 } });
      await page.route("https://nvelden.github.io/geneviewer-docs/**", (route) => {
        const file = path.join(root, new URL(route.request().url()).pathname.replace(/^\/geneviewer-docs/, ""));
        if (!fs.existsSync(file)) return route.fulfill({ status: 404, body: "" });
        return route.fulfill({
          status: 200,
          headers: { "Access-Control-Allow-Origin": "*" },
          contentType: "application/json",
          body: fs.readFileSync(file),
        });
      });
      await page.goto(`${origin}/404`).catch(() => {});
      await page.setContent("<!DOCTYPE html><html><body></body></html>");
      await page.addScriptTag({ content: library });
      if (setup) await page.addScriptTag({ content: setup });
      return page;
    };

    // Run a chart's JavaScript, gives what it draws
    const runCode = async (page, code) => {
      const size = /style="height: ([^"]+)"/.exec(code)?.[1] ?? "400px";
      return page.evaluate(async ({ code, size }) => {
        document.body.innerHTML = `<div id="chart" style="width: 688px; height: ${size}"></div>`;
        const AsyncFunction = (async () => {}).constructor;
        await new AsyncFunction(code)();
        return document.querySelectorAll("#chart .gene").length;
      }, { code, size });
    };

    for (const name of ["", "what-is-geneviewer", "getting-started", "examples", ...fs.readdirSync(path.join(__dirname, "..", "articles")).filter((file) => file.endsWith(".Rmd")).map((file) => `r/articles/${file.replace(".Rmd", "")}`)]) {
      const label = name || "home";
      const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
      const errors = [];
      page.on("pageerror", (error) => errors.push(error.message));
      page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
      await page.goto(base + name, { waitUntil: "networkidle" });
      // The charts draw when they come near the screen
      const height = await page.evaluate(() => document.documentElement.scrollHeight);
      for (let y = 0; y < height; y += 800) {
        await page.evaluate((top) => window.scrollTo(0, top), y);
        await page.waitForTimeout(30);
      }
      await page.waitForLoadState("networkidle");
      if (name === "") {
        const images = await page.evaluate(() => [...document.querySelectorAll(".gv-grid img")].map((img) => img.getAttribute("src")));
        expect(images.length > 0, `${label}: has a gallery (${images.length} tiles)`);
        for (const image of new Set(images)) {
          const response = await page.request.get(origin + image);
          expect(response.ok(), `${label}: ${image} loads`);
        }
        const hrefs = await page.evaluate(() => [...document.querySelectorAll(".VPHero .actions a")].map((a) => a.textContent.trim()));
        expect(hrefs.join() === "Get started,What is geneviewer?,Examples", `${label}: hero links (${hrefs})`);
        expect(errors.length === 0, `${label}: no console errors` + (errors.length ? ": " + errors.join("; ") : ""));
        await page.close();
        continue;
      }
      const charts = await page.evaluate(() => [...document.querySelectorAll(".gv-figure")].map((el) => ({
        id: el.dataset.chart,
        drawn: !!el.querySelector("svg.geneviewer-svg-content .gene, svg.geneviewer-svg-content path"),
        genes: el.querySelectorAll(".gene").length,
        error: el.querySelector(".gv-chart-error")?.textContent ?? null,
      })));
      expect(charts.length > 0, `${label}: has charts (${charts.length})`);
      const notDrawn = charts.filter((chart) => !chart.drawn || chart.error);
      expect(notDrawn.length === 0, `${label}: all ${charts.length} charts draw` +
        (notDrawn.length ? ` (not: ${notDrawn.map((chart) => `${chart.id} ${chart.error ?? ""}`).join(", ")})` : ""));

      // The toolbar shows while the mouse is over the chart
      const first = page.locator(".gv-chart").first();
      await first.scrollIntoViewIfNeeded();
      await first.hover();
      await page.waitForTimeout(300);
      const opacity = await first.locator(".geneviewer-toolbar").evaluate((node) => getComputedStyle(node).opacity);
      expect(opacity === "1", `${label}: hovering a chart shows its toolbar (opacity ${opacity})`);

      // The colour bar of the links stays clear of the genes
      const overBar = await page.evaluate(() => [...document.querySelectorAll(".gv-figure")].flatMap((figure) => {
        const parts = [...figure.querySelectorAll("svg.color-bar rect, svg.color-bar text")]
          .map((part) => part.getBoundingClientRect()).filter((box) => box.width);
        if (!parts.length) return [];
        const left = Math.min(...parts.map((box) => box.left));
        const right = Math.max(...parts.map((box) => box.right));
        const top = Math.min(...parts.map((box) => box.top));
        const bottom = Math.max(...parts.map((box) => box.bottom));
        // When zoomed, a gene is cut off where the plot area ends, 50 pixels from the edge
        const plotRight = figure.querySelector(".gv-chart").getBoundingClientRect().right - 50;
        const hit = [...figure.querySelectorAll(".gene")].map((gene) => gene.getBoundingClientRect())
          .some((box) => box.width && box.left < right && Math.min(box.right, plotRight) > left &&
            box.top < bottom && box.bottom > top);
        return hit ? [figure.dataset.chart] : [];
      }));
      expect(overBar.length === 0, `${label}: the colour bars are clear of the genes` +
        (overBar.length ? ` (not: ${overBar.join(", ")})` : ""));

      if (name === "what-is-geneviewer") {
        const gene = page.locator('[data-chart="interactive"] .gene').nth(1);
        await gene.scrollIntoViewIfNeeded();
        const box = await gene.boundingBox();
        await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
        const log = await page.locator(".gv-event-log").textContent();
        expect(/^select\s/m.test(log) && /^selection\s/m.test(log),
          `${label}: the event log shows a selection (${JSON.stringify(log.slice(0, 80))})`);
      }

      // The code of each chart: tabs JavaScript and R, and it runs
      const blocks = await page.evaluate(() => [...document.querySelectorAll(".gv-figure")].map((figure) => {
        let next = figure.nextElementSibling;
        if (next?.tagName === "DETAILS") next = next.querySelector(".vp-code-group");
        if (!next?.classList.contains("vp-code-group")) return { id: figure.dataset.chart, tabs: [] };
        return {
          id: figure.dataset.chart,
          tabs: [...next.querySelectorAll(".tabs label")].map((tab) => tab.textContent),
          code: [...next.querySelectorAll("pre code")].map((code) => code.textContent),
        };
      }));
      const withCode = blocks.filter((block) => block.tabs.length);
      expect(withCode.every((block) => block.tabs.join() === "JavaScript,R" &&
        block.code[0].includes("geneviewer.newChart(") && block.code[1].trim().length > 0),
        `${label}: ${withCode.length} charts show JavaScript and R code`);
      const setup = name === "getting-started"
        ? await page.evaluate(() => [...document.querySelectorAll("pre code")].map((code) => code.textContent)
          .find((text) => text.startsWith("const ophAClusters")))
        : "";
      if (name === "getting-started") expect(!!setup, `${label}: shows the shared tables`);
      const runner = await blankPage(setup);
      const wrong = [];
      for (const block of withCode) {
        const live = charts.find((chart) => chart.id === block.id);
        const genes = await runCode(runner, block.code[0]).catch((error) => `error: ${error.message}`);
        if (genes !== live.genes) wrong.push(`${block.id}: page ${live.genes} genes, code ${genes}`);
      }
      expect(wrong.length === 0, `${label}: the JavaScript of ${withCode.length} charts runs and draws as many genes` +
        (wrong.length ? ` (${wrong.slice(0, 8).join("; ")})` : ""));
      await runner.close();

      if (name === "examples") {
        // The sections of the R package's Examples page, all there
        const sections = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "site", ".vitepress", "examples.json"), "utf8"));
        const headings = await page.evaluate(() => [...document.querySelectorAll(".vp-doc h2")].map((h) => h.id));
        expect(sections.length === 10 && sections.every((section) => headings.includes(section.id[0])),
          `${label}: has the ${sections.length} sections of the R package's examples`);
      }
      expect(errors.length === 0, `${label}: no console errors` + (errors.length ? ": " + errors.join("; ") : ""));
      await page.close();
    }
    // The API reference lists every option of every component
    // The language switch: the text, the code tabs and "On this page" follow it,
    // and it is remembered
    {
      const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
      const lang = await context.newPage();
      const shown = (text) => lang.locator(`.vp-doc code:visible`, { hasText: text }).count();
      const activeTabs = () => lang.locator(".vp-code-group").evaluateAll((groups) => {
        const names = {};
        groups.forEach((group) => {
          const input = group.querySelector("input:checked");
          const name = input && group.querySelector(`label[for="${CSS.escape(input.id)}"]`).textContent.trim();
          names[name] = (names[name] ?? 0) + 1;
        });
        return names;
      });
      const outline = (text) => lang.locator(".VPDocAsideOutline a:visible", { hasText: text }).count();
      await lang.goto(`${base}getting-started`, { waitUntil: "networkidle" });
      expect(await shown("preventGeneOverlap") > 0 && await shown("prevent_gene_overlap") === 0, "language: JavaScript by default");
      expect(await outline("Shiny") === 0, "language: Shiny is not in the outline for JavaScript");
      const heading = lang.locator("#zoom");
      await heading.scrollIntoViewIfNeeded();
      const before = (await heading.boundingBox()).y;
      await lang.locator(".gv-language button", { hasText: /^R$/ }).first().click();
      await lang.waitForTimeout(300);
      expect(Math.abs((await heading.boundingBox()).y - before) < 5, "language: the page stays at the same place");
      expect(await shown("prevent_gene_overlap") > 0 && await shown("preventGeneOverlap") === 0, "language: the text shows the R names");
      const tabsR = await activeTabs();
      expect(tabsR.R > 50 && !tabsR.JavaScript, `language: every code tab shows R (${JSON.stringify(tabsR)})`);
      expect(await outline("Shiny") === 1, "language: Shiny is in the outline for R");
      await lang.reload({ waitUntil: "networkidle" });
      expect(await shown("prevent_gene_overlap") > 0 && (await activeTabs()).R > 50, "language: remembered after a reload");
      const jsTab = lang.locator(".vp-code-group .tabs label", { hasText: /^JavaScript$/ }).first();
      await jsTab.scrollIntoViewIfNeeded();
      await jsTab.click();
      await lang.waitForTimeout(300);
      const tabsJs = await activeTabs();
      expect(!tabsJs.R && await shown("preventGeneOverlap") > 0, `language: a code tab changes the whole page (${JSON.stringify(tabsJs)})`);
      await lang.goto(`${base}getting-started?lang=r#shiny`, { waitUntil: "networkidle" });
      await lang.waitForTimeout(300);
      const shiny = await lang.locator("#shiny").boundingBox();
      expect(!!shiny && shiny.y >= 0 && shiny.y < 800, "language: a link can set it and go to an R section");
      await context.close();
    }

    const schema = JSON.parse(fs.readFileSync(path.join(__dirname, "..", ".sources", "geneviewer-js", "schema", "spec-v1.schema.json"), "utf8"));
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(base + "api", { waitUntil: "load" });
    const listed = await page.evaluate(() => {
      const out = {};
      document.querySelectorAll("h3[id]").forEach((heading) => {
        let table = heading.nextElementSibling;
        while (table && table.tagName !== "TABLE" && !/^H[23]$/.test(table.tagName)) table = table.nextElementSibling;
        if (table && table.tagName !== "TABLE") table = null;
        out[heading.id] = table ? [...table.querySelectorAll("tr td:first-child code")].map((c) => c.textContent) : [];
      });
      return out;
    });
    const resolve = (node) => (node && node.$ref ? schema.$defs[node.$ref.split("/").pop()] : node);
    const entryOf = (node) => {
      const alternatives = node.oneOf || node.allOf || [node];
      return alternatives.map(resolve).find((alt) => alt && alt.properties) ||
        resolve(alternatives.find((alt) => alt.type === "array")?.items);
    };
    const missing = [];
    for (const [key, node] of Object.entries(schema.properties)) {
      const entry = entryOf(node);
      if (!entry || !entry.properties || ["version", "data", "width", "height", "style"].includes(key)) continue;
      for (const option of Object.keys(entry.properties)) {
        if (!(listed[key] || []).includes(option)) missing.push(`${key}.${option}`);
      }
    }
    expect(missing.length === 0, `api: every option of the schema is listed` +
      (missing.length ? ` (missing: ${missing.slice(0, 10).join(", ")})` : ""));
    expect(errors.length === 0, `api: no page errors`);
    await page.close();
  } finally {
    await browser.close();
    server.close();
  }
  console.log(`site: ${failures.length ? failures.length + " failed" : "all passed"}`);
  process.exit(failures.length ? 1 : 0);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
