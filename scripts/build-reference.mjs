// The body of the API reference page, from the schema
// (schema/spec-v1.schema.json of geneviewer-js): one section per component with each option's
// name, type, default and description; plus newChart(), the chart's methods,
// its events and the builds. The site puts it in site/api.md.
import { readFileSync } from "node:fs";

const schema = JSON.parse(readFileSync(".sources/geneviewer-js/schema/spec-v1.schema.json", "utf8"));
const { version } = JSON.parse(readFileSync("node_modules/geneviewer-js/package.json", "utf8"));

const escape = (text) => String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
// Markdown-like `code` in schema descriptions
const prose = (text) => escape(text || "").replace(/`([^`]+)`/g, "<code>$1</code>");

// Names of the shared types, as the reference shows them
const typeNames = {
  color: "colour", colors: "colours", style: "style object", itemStyle: "item styles",
  groupStyle: "styles by group", clusters: "clusters", clusterRef: "cluster", column: "column name",
  margin: "margins", scaleBreak: "break", data: "table", themeName: "theme name",
};

/** A short description of a schema node's type. */
function typeOf(node) {
  if (!node) return "";
  if (node.$ref) {
    const name = node.$ref.split("/").pop();
    return typeNames[name] ?? name;
  }
  if (node.allOf) return node.allOf.map(typeOf).join(", ");
  if (node.oneOf) return [...new Set(node.oneOf.map(typeOf))].join(" or ");
  if (node.enum) return node.enum.map((v) => JSON.stringify(v)).join(" | ");
  if ("const" in node) return JSON.stringify(node.const);
  if (node.type === "array") return `array of ${typeOf(node.items) || "values"}`;
  if (Array.isArray(node.type)) return node.type.join(" or ");
  if (node.type) return node.type;
  return "any";
}

const resolve = (node) => (node && node.$ref ? schema.$defs[node.$ref.split("/").pop()] : node);

/** The entry of a top-level component, and whether it may be an array. */
function entryOf(name) {
  const node = schema.properties[name];
  const alternatives = node.oneOf || node.allOf || [node];
  const entry = alternatives.map(resolve).find((alt) => alt && alt.type === "object" && alt.properties) ||
    resolve(alternatives.find((alt) => alt.type === "array")?.items);
  const many = !!(node.oneOf && node.oneOf.some((alt) => alt.type === "array")) || node.type === "array";
  return { node, entry, many };
}

function optionsTable(entry) {
  const rows = Object.entries(entry.properties).map(([key, option]) => {
    const def = "default" in option ? `<code>${escape(JSON.stringify(option.default))}</code>` : "";
    return `      <tr><td><code>${escape(key)}</code></td><td>${escape(typeOf(option))}</td><td>${def}</td><td>${prose(option.description)}</td></tr>`;
  });
  return `    <table class="options">
      <tr><th>Option</th><th>Type</th><th>Default</th><th>Description</th></tr>
${rows.join("\n")}
    </table>`;
}

// The components, in the order of the reference
const chartKeys = ["version", "data", "fields", "width", "height", "style"];
const components = Object.keys(schema.properties).filter((key) => !chartKeys.includes(key)).sort();

const chartRows = chartKeys.map((key) => {
  const option = schema.properties[key];
  const def = "default" in option ? `<code>${escape(JSON.stringify(option.default))}</code>` : "";
  return `      <tr><td><code>${key}</code></td><td>${escape(typeOf(option))}</td><td>${def}</td><td>${prose(option.description)}</td></tr>`;
}).join("\n");
const fields = resolve(schema.properties.fields);

const componentSections = components.map((key) => {
  const { node, entry, many } = entryOf(key);
  const shape = key === "theme"
    ? "A built-in theme's name, or an object."
    : many ? "One entry, or an array of entries applied in order." : "One object.";
  const extra = entry.additionalProperties ? "<p class=\"note\">Other options are passed to the renderer as they are.</p>" : "";
  return `    <h3 id="${key}"><code>${key}</code></h3>
    <p>${prose(node.description)} ${shape}</p>
${optionsTable(entry)}
    ${extra}`;
}).join("\n\n");

const body = `
    <h1>API reference</h1>
    <p class="lead">
      geneviewer ${version}: <code>newChart()</code>, the chart spec, the
      chart's methods and events. The spec's options are generated from the
      JSON Schema in the repository; names may still change until 1.0.
    </p>

    <ul class="toc">
      <li><a href="#newchart">newChart()</a></li>
      <li><a href="#functions">Other functions</a></li>
      <li><a href="#spec">The chart spec</a></li>
      <li><a href="#per-cluster">Per-cluster settings</a></li>
      <li><a href="#components">Components</a>: ${components.map((key) => `<a href="#${key}"><code>${key}</code></a>`).join(", ")}</li>
      <li><a href="#methods">Chart methods</a></li>
      <li><a href="#events">Events</a></li>
      <li><a href="#builds">Builds</a></li>
      <li><a href="#versions">Versions</a></li>
    </ul>

    <h2 id="newchart">newChart()</h2>
<pre><code>geneviewer.newChart(target, spec, options?) → Chart</code></pre>
    <table>
      <tr><th>Argument</th><th>Type</th><th>Description</th></tr>
      <tr><td><code>target</code></td><td>string or Element</td><td>A CSS selector or the element to draw in. The chart takes its size.</td></tr>
      <tr><td><code>spec</code></td><td>object</td><td>What to draw: see <a href="#spec">the chart spec</a>.</td></tr>
      <tr><td><code>options.on</code></td><td>object</td><td>Event handlers by name, added before the first draw, so they also get its events.</td></tr>
      <tr><td><code>options.saveAs</code></td><td>function</td><td>Called as <code>saveAs(blob, filename)</code> instead of the browser's download.</td></tr>
      <tr><td><code>options.injectStyles</code></td><td>boolean</td><td>Default <code>true</code>: the library adds its stylesheet to the page once. Turn off where a Content-Security-Policy blocks it, and load <code>geneviewer.css</code>.</td></tr>
      <tr><td><code>options.server</code></td><td>boolean</td><td>For the R and Python packages: events go to a server that may draw the chart again.</td></tr>
    </table>

    <h2 id="functions">Other functions</h2>
    <table>
      <tr><th>Name</th><th>Description</th></tr>
      <tr><td><code>geneviewer.compile(spec)</code></td><td>The render model a spec gives: clusters split, per-cluster settings applied, theme resolved. For tests and debugging.</td></tr>
      <tr><td><code>geneviewer.themes</code></td><td>The built-in themes and their settings.</td></tr>
      <tr><td><code>geneviewer.palettes</code></td><td>The built-in colour palettes.</td></tr>
      <tr><td><code>geneviewer.version</code></td><td>The library's version.</td></tr>
    </table>

    <h2 id="spec">The chart spec</h2>
    <p>
      A chart is one plain object, which can be written as JSON. Its keys
      mirror the R package's functions: <code>GC_labels()</code> becomes
      <code>labels</code>, and arguments become camelCase options.
    </p>
    <table class="options">
      <tr><th>Key</th><th>Type</th><th>Default</th><th>Description</th></tr>
${chartRows}
    </table>
    <h3 id="fields"><code>fields</code></h3>
${optionsTable(fields)}

    <h2 id="per-cluster">Per-cluster settings</h2>
    <p>
      Most components can be an array of entries. Entries apply in order; an
      entry with <code>clusters</code> applies only to those clusters, by name
      or by 1-based position:
    </p>
<pre><code>labels: [
  { label: "name" },                      // every cluster
  { clusters: ["dbophA"], show: false },  // then hide the labels of dbophA
]</code></pre>

    <h2 id="components">Components</h2>

${componentSections}

    <h2 id="methods">Chart methods</h2>
    <table>
      <tr><th>Method</th><th>Description</th></tr>
      <tr><td><code>update(partial)</code></td><td>Merge a partial spec into the spec and draw again: objects merge key by key; arrays, other values and tables (<code>data</code>, <code>links.data</code>) replace. <code>update({ theme: "dark" })</code> changes only the theme.</td></tr>
      <tr><td><code>setSpec(spec)</code></td><td>Replace the spec and draw again.</td></tr>
      <tr><td><code>getSpec()</code></td><td>A copy of the spec.</td></tr>
      <tr><td><code>on(name, handler)</code></td><td>Call <code>handler({ type, detail })</code> on each <a href="#events">event</a> of that name. Returns a function that stops it.</td></tr>
      <tr><td><code>off(name, handler)</code></td><td>Stop calling a handler.</td></tr>
      <tr><td><code>zoomTo([start, end])</code></td><td>Set the zoom window, in the units of <code>zoom.mode</code>; <code>zoomTo(null)</code> shows everything.</td></tr>
      <tr><td><code>select(items)</code></td><td>Select elements, as a click does, and report <code>select</code> and <code>selection</code> when that changes the selection. An item gives a <code>component</code> and any of <code>cluster</code>, <code>part</code> and <code>data</code>; it selects every drawn element that matches all it gives, so <code>{ component: "genes", data: { rowID: 3 } }</code> selects gene row 3, and the items of <code>getSelection()</code> select their elements again. <code>select(null)</code> or <code>select([])</code> clears it. Needs <code>events: { select: true }</code>.</td></tr>
      <tr><td><code>getSelection()</code></td><td>The selected elements, as the <code>selection</code> event reports them.</td></tr>
      <tr><td><code>undo()</code>, <code>redo()</code></td><td>Undo or redo the last move, as the toolbar does (<code>events: { drag: true }</code>).</td></tr>
      <tr><td><code>download(format, filename)</code></td><td>Save the chart as <code>"svg"</code> or <code>"png"</code>, as the save menu does: through the <code>saveAs</code> option, or as a browser download. The name defaults to <code>graph.svg</code> or <code>graph.png</code>. A Promise.</td></tr>
      <tr><td><code>toSVG()</code></td><td>The chart as SVG text.</td></tr>
      <tr><td><code>toPNG()</code></td><td>The chart as a PNG <code>Blob</code> (a Promise).</td></tr>
      <tr><td><code>resize()</code></td><td>Draw again at the element's size.</td></tr>
      <tr><td><code>destroy()</code></td><td>Remove the chart and its listeners.</td></tr>
    </table>

    <h2 id="events">Events</h2>
    <p>
      Handlers get <code>{ type, detail }</code>. Each event is also sent as a
      DOM event, <code>geneviewer:&lt;name&gt;</code>, on the chart's element;
      see the <a href="what-is-geneviewer.html">interactive example</a>.
      <code>events</code> in the spec turns them on.
    </p>
    <table>
      <tr><th>Event</th><th>When</th></tr>
      <tr><td><code>click</code></td><td>An element was clicked (<code>events.click</code>).</td></tr>
      <tr><td><code>dblclick</code></td><td>An element was double-clicked (<code>events.dblclick</code>).</td></tr>
      <tr><td><code>select</code></td><td>The selected element changed (<code>events.select</code>).</td></tr>
      <tr><td><code>selection</code></td><td>The list of selected elements changed.</td></tr>
      <tr><td><code>drag</code>, <code>dragmove</code></td><td>An element was moved, or is being moved (<code>events.drag</code>).</td></tr>
      <tr><td><code>moves</code></td><td>Several elements were moved at once, or a move was undone or redone.</td></tr>
      <tr><td><code>zoom</code></td><td>The zoom window changed (<code>events.zoom</code>).</td></tr>
      <tr><td><code>rendered</code></td><td>The chart was drawn (<code>events.rendered</code>).</td></tr>
    </table>

    <h2 id="builds">Builds</h2>
    <table>
      <tr><th>File</th><th>Format</th><th>D3</th><th>For</th></tr>
      <tr><td><code>geneviewer.min.js</code></td><td>Script tag, global <code>geneviewer</code>; minified, source map</td><td>included</td><td>CDNs and plain HTML pages</td></tr>
      <tr><td><code>geneviewer.mjs</code></td><td>ES module (<code>import ... from "geneviewer-js"</code>)</td><td>imported from npm</td><td>Bundlers</td></tr>
      <tr><td><code>geneviewer.standalone.mjs</code></td><td>ES module (<code>geneviewer-js/standalone</code>), minified</td><td>included</td><td>Browser <code>import</code>, Jupyter</td></tr>
      <tr><td><code>geneviewer.core.js</code></td><td>Script tag, not minified</td><td>the page's <code>d3</code></td><td>The R package</td></tr>
      <tr><td><code>geneviewer.css</code></td><td>Stylesheet</td><td></td><td>Pages that turn off <code>injectStyles</code></td></tr>
      <tr><td><code>geneviewer.d.ts</code>, <code>spec.d.ts</code></td><td>TypeScript types</td><td></td><td>Editors and TypeScript</td></tr>
    </table>

    <h2 id="versions">Versions</h2>
    <ul>
      <li><strong>Library:</strong> semantic versioning from 1.0. While on 0.x,
        minor versions may change the API.</li>
      <li><strong>Spec:</strong> the optional <code>version</code> key. A spec
        without one is version 1, the only version so far. A spec with a newer
        version than the library knows is drawn as far as possible, with a
        warning in the console.</li>
    </ul>
`;

/** @returns {string} The HTML of the page. */
export const referenceHtml = () => body;
