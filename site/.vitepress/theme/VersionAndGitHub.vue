<script setup>
import { usePageLanguage } from "./language.js";

const current = usePageLanguage();
</script>

<template>
  <div class="gv-nav-links">
    <a :href="current.versionLink" target="_blank" rel="noreferrer" :title="current.versionTitle">{{ current.version }}</a>
    <a :href="current.repo" target="_blank" rel="noreferrer" :title="`${current.repoName} on GitHub`">GitHub</a>
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
