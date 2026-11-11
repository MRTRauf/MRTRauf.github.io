"""Static integrity, link, accessibility and basic contrast checks for the public portfolio."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
MIRROR = ROOT / "gallery.html"
STYLE = ROOT / "style.css"
JS = ROOT / "site.js"
EXPECTED_PROJECTS = {
    "touchline-ai", "clubops-intelligence-public", "network-kpi-anomaly-detector",
    "predictive-maintenance-rul", "science-trend-radar",
    "network-slicing-decision-support-tool", "bluesky-polarization-coordination",
    "patent_prior_screening", "drinking-water-quality-prediction",
    "l1-ml-signal-analytics", "ip_deadline_tracker",
}

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.anchors = []
        self.local_links = []
        self.cards = []
        self.project_categories = set()
        self.uses = []
        self.symbols = set()
        self.external_scripts = []
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "symbol" and attrs.get("id"):
            self.symbols.add(attrs["id"])
        if tag == "use" and attrs.get("href", "").startswith("#"):
            self.uses.append(attrs["href"][1:])
        if tag == "script" and attrs.get("src"):
            self.external_scripts.append(attrs["src"])
        if tag == "a":
            href = attrs.get("href", "")
            if href.startswith("#"):
                self.anchors.append(href[1:])
            if "project-card" in attrs.get("class", "").split():
                self.cards.append(href)
                self.project_categories.add(attrs.get("data-category"))
                assert attrs.get("target") == "_blank", "Project tile must open source in new tab"
                assert {"noopener", "noreferrer"} <= set(attrs.get("rel", "").split()), "Unsafe external tile"
            if href and not href.startswith(("https://", "mailto:", "#")):
                self.local_links.append(href)
        if tag in ("link", "script") and attrs.get("href") and not attrs["href"].startswith(("https://", "#")):
            self.local_links.append(attrs["href"])
        if tag == "script" and attrs.get("src"):
            self.local_links.append(attrs["src"])

def color_value(s):
    s = s.lstrip("#")
    rgb = [int(s[i:i+2], 16)/255 for i in (0,2,4)]
    linear = [v/12.92 if v <= 0.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return sum(a*b for a,b in zip(linear, (.2126, .7152, .0722)))

def contrast(foreground, background):
    a, b = sorted((color_value(foreground), color_value(background)), reverse=True)
    return (a+.05)/(b+.05)

def vars_for(text, selector):
    match = re.search(re.escape(selector) + r"\s*\{([^}]+)\}", text)
    assert match, f"Missing palette {selector}"
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", match.group(1)))

def main():
    html = HOME.read_text(encoding="utf-8")
    assert html == MIRROR.read_text(encoding="utf-8"), "gallery.html should mirror the homepage"
    css = STYLE.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    page = Page()
    page.feed(html)
    assert len(page.ids) == len(set(page.ids)), "Duplicate HTML IDs"
    assert not (set(page.anchors) - set(page.ids)), "Broken internal navigation"
    assert not (set(page.uses) - page.symbols), "Unresolved icon sprite IDs"
    assert page.external_scripts == ["site.js"], "Unexpected scripts"
    assert len(page.cards) == len(EXPECTED_PROJECTS), "Unexpected icon card count"
    assert set(page.cards) == {f"https://github.com/MRTRauf/{name}" for name in EXPECTED_PROJECTS}
    assert page.project_categories == {"football", "networks", "ml", "research", "ip"}
    for name in page.local_links:
        assert (ROOT / name).is_file(), f"Missing local asset: {name}"
    assert 'id="project-search"' in html and 'id="result-status"' in html
    assert 'aria-live="polite"' in html and 'class="skip-link"' in html
    assert 'name="description"' in html and 'rel="canonical"' in html
    assert 'FEATURED DEEP DIVE / TOUCHLINE AI' not in html
    assert 'window.TOUCHLINE_CONFIG' not in js
    for phrase in ["setCategory", "setTheme", "resetFilters", "data-view-button"]:
        assert phrase in js
    for phrase in ["@media", "prefers-reduced-motion", "focus-visible", ".project-card", "grid-template-columns"]:
        assert phrase in css
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert ld and json.loads(ld.group(1))["@type"] == "Person"
    for theme in (":root", ':root[data-theme="light"]'):
        vals = vars_for(css, theme)
        for fore, bg in (("ink", "bg"), ("muted", "surface"), ("accent-ink", "accent")):
            actual = contrast(vals[fore], vals[bg])
            assert actual >= 4.5, f"WCAG contrast {theme} {fore}/{bg}: {actual:.2f}"
    print("PASS: 11 public repository icons, assets, anchors, icons, metadata, interactions, theme contrast, duplicate gallery")

if __name__ == "__main__":
    main()
