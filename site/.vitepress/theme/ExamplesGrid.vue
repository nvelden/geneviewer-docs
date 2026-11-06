<script setup>
// The tilted honeycomb of charts on the home page, after the gallery of the
// D3 docs (ExamplesGrid.vue, d3/d3, ISC licence). The thumbnails are made by
// scripts/site-gallery.mjs from the charts of the site.
import { onMounted, onUnmounted, ref, shallowRef } from "vue";
import { withBase } from "vitepress";
import gallery from "../gallery.json";

const container = ref();
const columns = ref(10);
const rows = ref(5);
const cells = shallowRef([]);
const pointer = ref(0.5);

let observer;
let frame;
let clientX = 0;

function layout() {
  const width = parseFloat(getComputedStyle(container.value).getPropertyValue("--grid-width"));
  columns.value = Math.ceil(document.body.clientWidth / width) + 3;
  rows.value = Math.round(640 / width + 2);
  const count = columns.value * rows.value;
  cells.value = Array.from({ length: count }, (_, i) => {
    const column = i % columns.value;
    const row = Math.floor(i / columns.value);
    return {
      key: i,
      // Neighbours differ: odd rows start further along the list
      item: gallery[(i + row * 7) % gallery.length],
      x: column - columns.value / 2 + (row % 2) * 0.5,
      y: row - rows.value / 2,
      delay: (column / columns.value + ((i * 37) % 11) / 11 - 0.4).toFixed(2),
    };
  });
}

function onPointerMove(event) {
  clientX = event.clientX;
  if (!frame) {
    frame = requestAnimationFrame(() => {
      frame = null;
      pointer.value = clientX / document.body.clientWidth;
    });
  }
}

onMounted(() => {
  observer = new ResizeObserver(layout);
  observer.observe(document.body);
  addEventListener("pointermove", onPointerMove);
});

onUnmounted(() => {
  observer.disconnect();
  removeEventListener("pointermove", onPointerMove);
  cancelAnimationFrame(frame);
});
</script>

<template>
  <div ref="container" class="gv-grid" :style="{ transform: `translate(${60 - pointer * 10}vw, 33%)` }">
    <div v-for="cell in cells" :key="cell.key" class="gv-cell" :style="{ '--delay': `${cell.delay}s` }">
      <a
        :href="withBase(cell.item.link)"
        :title="cell.item.title"
        :style="{ '--x': cell.x, '--y': cell.y }"
      >
        <img :src="withBase(cell.item.image)" :alt="cell.item.title" loading="lazy" width="320" height="320" />
      </a>
    </div>
  </div>
</template>

<style scoped>
.gv-grid {
  position: relative;
  height: 640px;
  transition: transform 150ms ease-out;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
  --grid-width: 140px;
}

@media (min-width: 640px) {
  .gv-grid {
    --grid-width: 160px;
  }
}

@media (min-width: 960px) {
  .gv-grid {
    --grid-width: 200px;
  }
}

/* The shadow is on this box, as the hexagon clip of the link would cut it */
.gv-cell {
  position: relative;
  transition: filter 250ms ease-out;
  animation: gv-fade-in 350ms cubic-bezier(0.215, 0.61, 0.355, 1) var(--delay) backwards;
}

.gv-cell:hover {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.4));
  z-index: 3;
}

a {
  position: absolute;
  --transform: perspective(75em) rotateX(30deg) rotateZ(-7deg)
    translate(calc(var(--x) * 100%), calc(var(--y) * 86.67%)) scale(1.145);
  transform: var(--transform);
  animation: gv-drop-in 350ms cubic-bezier(0.215, 0.61, 0.355, 1) var(--delay) backwards;
  transition: transform 250ms ease-out;
  clip-path: polygon(50% 100%, 93.3% 75%, 93.3% 25%, 50% 0, 6.7% 25%, 6.7% 75%);
}

a:hover {
  transform: var(--transform) translateZ(10px) scale(1.1);
}

img {
  aspect-ratio: 1;
  object-fit: cover;
  width: var(--grid-width);
  max-width: none;
}

@media (prefers-reduced-motion: reduce) {
  .gv-grid,
  .gv-cell,
  a {
    animation: none;
    transition: none;
  }
}

@keyframes gv-fade-in {
  from {
    filter: blur(20px);
    opacity: 0;
  }
  to {
    filter: none;
    opacity: 1;
  }
}

@keyframes gv-drop-in {
  from {
    transform: var(--transform) translateY(-100px) translateZ(400px);
  }
  to {
    transform: var(--transform);
  }
}
</style>
