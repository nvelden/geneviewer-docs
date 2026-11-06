// The language the guide is read in. The pages hold the text of every language
// (.lang-js, .lang-r; see "Writing for each language" in the README) and the
// attribute on <html> shows one. To add a language, add it here and in custom.css.
import { ref } from "vue";

export const languages = [
  { id: "js", label: "JavaScript" },
  { id: "r", label: "R" },
];

export const language = ref("js");

// Show the code tab of the language in every chart. Other tabs, such as npm and
// yarn, are left alone.
function syncTabs() {
  const tab = languages.find((entry) => entry.id === language.value).label;
  document.querySelectorAll(".vp-code-group").forEach((group) => {
    const label = [...group.querySelectorAll(".tabs label")].find((node) => node.textContent.trim() === tab);
    const input = label && group.querySelector(`#${CSS.escape(label.htmlFor)}`);
    if (input && !input.checked) input.click();
  });
}

// A heading of another language has no place in "On this page"
function syncOutline() {
  document.querySelectorAll(".vp-doc :is(.lang-js, .lang-r) :is(h2, h3)").forEach((heading) => {
    const link = document.querySelector(`.VPDocAsideOutline a[href="#${CSS.escape(heading.id)}"]`);
    if (link) link.parentElement.hidden = heading.offsetParent === null;
  });
}

/** Bring the page in line with the language, after a load or a change of page. */
export function syncLanguage() {
  language.value = document.documentElement.dataset.lang || "js";
  syncTabs();
  syncOutline();
}

/** Change the language. What is on screen stays where it is, also in a long page. */
export function setLanguage(id, anchor) {
  if (id === language.value) return;
  const element = anchor ?? document.elementFromPoint(innerWidth / 2, innerHeight / 2);
  const before = element?.getBoundingClientRect().top;
  document.documentElement.dataset.lang = id;
  try {
    localStorage.setItem("geneviewer-language", id);
  } catch {
    // Without storage the language lasts until the page is left
  }
  syncLanguage();
  if (element?.isConnected && element.offsetParent !== null) {
    scrollBy(0, element.getBoundingClientRect().top - before);
  }
}

/** A click on the code tab of a language changes the language of the page. */
export function listenToTabs() {
  document.addEventListener("change", ({ target }) => {
    if (!target.matches?.(".vp-code-group input")) return;
    const group = target.closest(".vp-code-group");
    const label = group.querySelector(`label[for="${CSS.escape(target.id)}"]`)?.textContent.trim();
    const entry = languages.find((item) => item.label === label);
    if (entry) setLanguage(entry.id, group);
  });
}
