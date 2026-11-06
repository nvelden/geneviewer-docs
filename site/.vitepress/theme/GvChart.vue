<script setup>
// A live chart, drawn from site/public/charts/<id>.json when it comes near the
// screen: the long pages have many charts.
import { onMounted, onUnmounted, ref } from "vue";
import { withBase } from "vitepress";

const props = defineProps({
  id: { type: String, required: true },
  height: { type: String, default: "400px" },
  width: { type: String, default: "100%" },
  // Show the chart's events below it
  log: { type: Boolean, default: false },
});

const events = ["select", "selection", "dblclick", "drag", "moves", "zoom"];
const element = ref();
const error = ref("");
const logText = ref("");

let chart;
let visibility;
let sizes;
let unmounted = false;

// A short, one-line view of an event's detail
function summary(detail) {
  const text = JSON.stringify(detail, (key, value) => (key === "style" ? undefined : value));
  return text && text.length > 160 ? `${text.slice(0, 157)}...` : text;
}

async function draw() {
  try {
    const [library, response] = await Promise.all([
      import("geneviewer-js/standalone"),
      fetch(withBase(`/charts/${props.id}.json`)),
    ]);
    if (!response.ok) throw new Error(`could not load ${props.id}`);
    const { spec } = await response.json();
    if (unmounted) return;
    const on = {};
    if (props.log) {
      for (const name of events) {
        on[name] = (event) => {
          logText.value = `${event.type}  ${summary(event.detail)}\n${logText.value}`;
        };
      }
    }
    chart = library.newChart(element.value, spec, { on });
    let width = element.value.clientWidth;
    sizes = new ResizeObserver(() => {
      if (element.value.clientWidth === width) return;
      width = element.value.clientWidth;
      chart.resize();
    });
    sizes.observe(element.value);
  } catch (e) {
    error.value = `The chart could not be drawn: ${e.message}`;
  }
}

onMounted(() => {
  visibility = new IntersectionObserver((entries) => {
    if (!entries.some((entry) => entry.isIntersecting)) return;
    visibility.disconnect();
    draw();
  }, { rootMargin: "800px" });
  visibility.observe(element.value);
});

onUnmounted(() => {
  unmounted = true;
  visibility?.disconnect();
  sizes?.disconnect();
  chart?.destroy();
});
</script>

<template>
  <figure class="gv-figure vp-raw" :data-chart="id">
    <div ref="element" class="gv-chart" :style="{ height, width, maxWidth: '100%' }"></div>
    <p v-if="error" class="gv-chart-error">{{ error }}</p>
    <pre v-if="log" class="gv-event-log" aria-live="polite">{{ logText || "Click a gene, or drag the slider..." }}</pre>
  </figure>
</template>
