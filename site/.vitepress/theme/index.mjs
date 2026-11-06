import DefaultTheme from "vitepress/theme-without-fonts";
import GvChart from "./GvChart.vue";
import SiteLayout from "./SiteLayout.vue";
import "./custom.css";

export default {
  extends: DefaultTheme,
  Layout: SiteLayout,
  enhanceApp({ app }) {
    app.component("GvChart", GvChart);
  },
};
