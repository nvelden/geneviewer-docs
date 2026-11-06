<script setup>
const version = __APP_VERSION__;
const repo = "https://github.com/nvelden/geneviewer-js";
</script>

<template>
  <div class="gv-nav-links">
    <a :href="`${repo}/releases`" target="_blank" rel="noreferrer" :title="`${version} release notes`">{{ version }}</a>
    <a :href="repo" target="_blank" rel="noreferrer" title="geneviewer-js on GitHub">GitHub</a>
  </div>
</template>

<style scoped>
.gv-nav-links {
  display: flex;
  gap: 1rem;
  margin-left: 1rem;
}

a {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  transition: color 0.25s;
}

a:hover {
  color: var(--vp-c-brand-1);
}

@media (max-width: 560px) {
  a:first-child {
    display: none;
  }
}
</style>
