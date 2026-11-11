"use strict";
const config = window.TOUCHLINE_CONFIG;
if (config?.dashboardUrlVerified === true && typeof config.dashboardUrl === "string") {
  try {
    const url = new URL(config.dashboardUrl);
    if (url.protocol === "https:" && url.hostname.endsWith(".streamlit.app") && !url.username && !url.password) {
      const link = document.getElementById("dashboard");
      link.href = url.href; link.textContent = "Open interactive dashboard ↗";
      document.getElementById("release-status").textContent = "The interactive dashboard is available. Explore profiles, comparisons and the saved forecasting research.";
    }
  } catch { /* Keep the honest unavailable state for invalid configuration. */ }
}

if (config?.githubUrlVerified === true && config.githubUrl === "https://github.com/MRTRauf/touchline-ai") {
  const status = document.getElementById("github-status");
  const link = document.createElement("a"); link.href = config.githubUrl; link.textContent = "Explore the public GitHub showcase ↗";
  status.replaceChildren(link);
}
