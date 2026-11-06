<script setup>
import { nextTick, onMounted } from "vue";
import { onContentUpdated } from "vitepress";
import DefaultTheme from "vitepress/theme-without-fonts";
import ExamplesGrid from "./ExamplesGrid.vue";
import LanguageSwitch from "./LanguageSwitch.vue";
import VersionAndGitHub from "./VersionAndGitHub.vue";
import { listenToTabs, syncLanguage } from "./language.js";

const { Layout } = DefaultTheme;

onMounted(() => {
  listenToTabs();
  syncLanguage();
  // Showing other tabs moves what is below them: go back to the section linked to
  if (location.hash) document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView();
});
onContentUpdated(() => nextTick(syncLanguage));
</script>

<template>
  <Layout>
    <template #home-features-before>
      <ExamplesGrid />
    </template>
    <template #nav-bar-content-after>
      <LanguageSwitch />
      <VersionAndGitHub />
    </template>
    <template #nav-screen-content-after>
      <LanguageSwitch />
    </template>
  </Layout>
</template>
