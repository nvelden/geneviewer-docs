<script setup>
import { language, languages, setLanguage } from "./language.js";
</script>

<template>
  <div class="gv-language" role="group" aria-label="Language of the guide">
    <button
      v-for="entry in languages"
      :key="entry.id"
      type="button"
      :aria-pressed="language === entry.id"
      @click="setLanguage(entry.id)"
    >{{ entry.label }}</button>
  </div>
</template>

<style scoped>
.gv-language {
  display: inline-flex;
  margin-left: 1rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  overflow: hidden;
}

button {
  padding: 2px 10px;
  font-size: 13px;
  font-weight: 500;
  line-height: 24px;
  color: var(--vp-c-text-2);
}

button:hover {
  color: var(--vp-c-text-1);
}

button[aria-pressed="true"] {
  color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
}
</style>
