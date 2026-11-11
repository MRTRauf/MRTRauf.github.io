"use strict";

/* Static, privacy-friendly portfolio interactions. No API, trackers or dependencies. */
(() => {
  const root = document.documentElement;
  const cards = [...document.querySelectorAll(".project-card")];
  const search = document.querySelector("#project-search");
  const filters = [...document.querySelectorAll("[data-category-filter]")];
  const resultStatus = document.querySelector("#result-status");
  const empty = document.querySelector("#empty-state");
  const clearSearch = document.querySelector("#clear-search");
  const reset = document.querySelector("#reset-projects");
  const themeButton = document.querySelector("#theme-toggle");
  const viewButtons = [...document.querySelectorAll("[data-view-button]")];
  const projectGrid = document.querySelector("#project-grid");
  const year = document.querySelector("#year");
  let category = "all";

  if (year) year.textContent = String(new Date().getFullYear());

  // Text searches use only labels, descriptions, tags, and user-visible category metadata.
  const normalize = value => String(value || "").toLocaleLowerCase().normalize("NFKD");
  function render() {
    const query = normalize(search?.value.trim());
    let shown = 0;
    cards.forEach(card => {
      const matchesCategory = category === "all" || card.dataset.category === category;
      const matchesQuery = !query || normalize(card.dataset.search || card.textContent).includes(query);
      const visible = matchesCategory && matchesQuery;
      card.hidden = !visible;
      if (visible) shown++;
    });
    if (resultStatus) resultStatus.textContent = `${shown} of ${cards.length} projects`;
    if (empty) empty.hidden = shown !== 0;
    if (clearSearch) clearSearch.hidden = !search?.value;
  }

  function setCategory(next) {
    category = next;
    filters.forEach(button => {
      const active = button.dataset.categoryFilter === next;
      button.setAttribute("aria-pressed", String(active));
    });
    render();
  }

  function resetFilters() {
    if (search) search.value = "";
    setCategory("all");
  }

  filters.forEach(button => button.addEventListener("click", () => setCategory(button.dataset.categoryFilter)));
  search?.addEventListener("input", render);
  clearSearch?.addEventListener("click", () => { if (search) { search.value = ""; search.focus(); } render(); });
  reset?.addEventListener("click", () => { resetFilters(); search?.focus(); });

  // Native, reversible list view for users who prefer more compact reading.
  viewButtons.forEach(button => button.addEventListener("click", () => {
    const mode = button.dataset.viewButton === "list" ? "list" : "grid";
    if (projectGrid) projectGrid.dataset.view = mode;
    viewButtons.forEach(b => b.setAttribute("aria-pressed", String(b === button)));
  }));

  // Theme is an optional local-only preference; no analytics or remote storage.
  let initialTheme = "dark";
  try { if (localStorage.getItem("mrtrauf-theme") === "light") initialTheme = "light"; } catch (_) {}
  function setTheme(theme) {
    root.dataset.theme = theme;
    if (themeButton) {
      themeButton.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
      themeButton.setAttribute("title", theme === "dark" ? "Light theme" : "Dark theme");
      themeButton.setAttribute("aria-pressed", String(theme === "light"));
      const text = themeButton.querySelector(".theme-label");
      if (text) text.textContent = theme === "dark" ? "Light" : "Dark";
    }
  }
  setTheme(initialTheme);
  themeButton?.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    setTheme(next);
    try { localStorage.setItem("mrtrauf-theme", next); } catch (_) {}
  });

  document.addEventListener("keydown", event => {
    const element = document.activeElement;
    const typing = element && (element.matches("input, textarea, select") || element.isContentEditable);
    if (event.key === "/" && !typing && !event.ctrlKey && !event.metaKey && !event.altKey) {
      event.preventDefault(); search?.focus();
    }
    if (event.key === "Escape" && element === search && search?.value) { search.value = ""; render(); }
  });

  render();
})();
