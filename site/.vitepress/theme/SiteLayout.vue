<script setup>
import DefaultTheme from "vitepress/theme-without-fonts";
import ExamplesGrid from "./ExamplesGrid.vue";
import VersionAndGitHub from "./VersionAndGitHub.vue";

const { Layout } = DefaultTheme;
</script>

<template>
  <Layout>
    <template #home-features-before>
      <ExamplesGrid />
    </template>
    <template #nav-bar-content-after>
      <VersionAndGitHub />
    </template>
  </Layout>
</template>
