<script setup>
import { withBase } from "vitepress";
</script>

<template>
  <footer class="gv-footer">
    <div class="gv-footer-columns">
      <a class="gv-footer-brand" :href="withBase('/')" title="Home">
        <img :src="withBase('/logo.png')" alt="" height="32" style="height: 32px; width: auto" />
        <span>geneviewer</span>
      </a>
      <div>
        <div class="gv-footer-title">Resources</div>
        <ul>
          <li><a target="_blank" rel="noreferrer" href="https://github.com/nvelden/geneviewer-js/issues">Issues</a></li>
          <li><a target="_blank" rel="noreferrer" href="https://github.com/nvelden/geneviewer-js/releases">Releases</a></li>
          <li><a target="_blank" rel="noreferrer" href="https://www.npmjs.com/package/geneviewer-js">npm</a></li>
          <li><a target="_blank" rel="noreferrer" href="https://github.com/nvelden/geneviewer-js/blob/main/docs/roadmap.md">Roadmap</a></li>
        </ul>
      </div>
      <div>
        <div class="gv-footer-title">geneviewer</div>
        <ul>
          <li><a target="_blank" rel="noreferrer" href="https://nvelden.github.io/geneviewer/">R package</a></li>
          <li><a target="_blank" rel="noreferrer" href="https://cran.r-project.org/package=geneviewer">CRAN</a></li>
          <li><a target="_blank" rel="noreferrer" href="https://nvelden.github.io/geneviewer-shinylive/">Gene Cluster Dashboard</a></li>
        </ul>
      </div>
    </div>
    <div class="gv-footer-legal">
      © {{ new Date().getUTCFullYear() }} geneviewer authors.
      <a target="_blank" rel="noreferrer" href="https://github.com/nvelden/geneviewer-js/blob/main/LICENSE.md">MIT License</a>.
      Charts are drawn with <a target="_blank" rel="noreferrer" href="https://d3js.org">D3</a>.
    </div>
  </footer>
</template>

<style>
.gv-footer {
  background: var(--vp-c-bg-alt);
  font-size: 12px;
  line-height: normal;
  padding: 2rem;
}

.gv-footer-columns {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem 4rem;
  margin-bottom: 2rem;
}

.gv-footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  align-self: flex-start;
  flex-basis: 30%;
  font-size: 16px;
  font-weight: 600;
}

.gv-footer-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.gv-footer li {
  margin-bottom: 0.5rem;
}

.gv-footer a:hover {
  text-decoration: underline;
}

.gv-footer-legal a {
  color: var(--vp-c-brand-1);
}

/* The docs pages have the sidebar and no footer */
.has-sidebar ~ .gv-footer {
  display: none;
}
</style>
