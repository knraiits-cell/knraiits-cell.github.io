#!/usr/bin/env python3
"""
netineti charaiveti charaiveti — multi-jurisdiction site builder
================================================================

Reads:
    _source/index.template.html
    _source/style.css
    _source/main.js
    _source/assets/
    _source/variants.json

Emits, one directory per variant in `_build/`:
    _build/main/                    (replicates the GitHub Pages main site)
    _build/mirror/                  (replicates the GitHub Pages mirror site)
    _build/perplexity_primary/      (Perplexity-deployed primary)
    _build/perplexity_dr/           (Perplexity-deployed DR)

Each directory contains a complete, self-contained static site:
    index.html, css/style.css, js/main.js, assets/, robots.txt, _headers, offline.html

Usage:
    python3 _source/build.py            # builds all variants
    python3 _source/build.py --variant main mirror     # builds only listed variants

This script has NO third-party dependencies — pure Python 3 stdlib. It works in
GitHub Actions out-of-the-box.
"""

import json
import shutil
import sys
import hashlib
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # _source/
REPO = ROOT.parent                              # repo root
BUILD_DIR = REPO / "_build"

# ── Variant-specific blocks (HTML & JS fragments) ─────────────────────────

DR_RIBBON_BLOCK_TEMPLATE = """<!-- DR mirror ribbon -->
<div class="dr-ribbon" role="status" aria-live="polite">
  <span data-en="{en}" data-hi="{hi}">{en}</span>
  <span class="sep">·</span>
  <a href="https://netineticharaiveticharaiveti.in" rel="noopener"
     data-en="{link_en}"
     data-hi="{link_hi}">{link_en}</a>
</div>
"""

FOOTER_MAIN_POINTS_TO_MIRROR = """  <!-- Mirror / fallback site —  GitHub Pages -->
  <p class="footer-mirror"
     data-en="Mirror site: <a href=&quot;https://knraiits-cell.github.io/netineti-mirror&quot; target=&quot;_blank&quot; rel=&quot;noopener nofollow&quot;>knraiits-cell.github.io/netineti-mirror</a> — use this if the main site is unreachable."
     data-hi="वैकल्पिक स्थल: <a href=&quot;https://knraiits-cell.github.io/netineti-mirror&quot; target=&quot;_blank&quot; rel=&quot;noopener nofollow&quot;>knraiits-cell.github.io/netineti-mirror</a> — यदि मुख्य स्थल न खुल पाए तो यहाँ पधारें।">
    Mirror site: <a href="https://knraiits-cell.github.io/netineti-mirror" target="_blank" rel="noopener nofollow">knraiits-cell.github.io/netineti-mirror</a> — use this if the main site is unreachable.
  </p>"""

FOOTER_MIRROR_POINTS_TO_MAIN = """  <!-- This IS the mirror — link back to the canonical/main site -->
  <p class="footer-mirror"
     data-en="You are on the mirror site. Main site: <a href=&quot;https://netineticharaiveticharaiveti.in&quot; rel=&quot;noopener&quot;>netineticharaiveticharaiveti.in</a>"
     data-hi="आप मिरर स्थल पर हैं। मुख्य स्थल: <a href=&quot;https://netineticharaiveticharaiveti.in&quot; rel=&quot;noopener&quot;>netineticharaiveticharaiveti.in</a>">
    You are on the mirror site. Main site: <a href="https://netineticharaiveticharaiveti.in" rel="noopener">netineticharaiveticharaiveti.in</a>
  </p>"""


def render_html(template: str, v: dict) -> str:
    """Substitute {{TOKEN}} placeholders for one variant."""
    repl = {
        "TITLE":               v["title"],
        "CSP_CONNECT_SRC":     v["csp_connect_src"],
        "ROBOTS":              v["robots"],
        "ROBOTS_EXTRA_META":   v.get("robots_extra_meta", ""),
        "FP_SUFFIX":           v.get("fingerprint_suffix", ""),
    }

    # Schema.org mirror entry — only main + perplexity_primary point to the mirror
    if v.get("schema_same_as_mirror"):
        repl["SCHEMA_MIRROR_ENTRY"] = ',\n    "https://knraiits-cell.github.io/netineti-mirror"'
    else:
        repl["SCHEMA_MIRROR_ENTRY"] = ""

    # DR ribbon block (only on mirror variants)
    if v.get("show_dr_ribbon"):
        repl["DR_RIBBON_BLOCK"] = DR_RIBBON_BLOCK_TEMPLATE.format(
            en=v["dr_ribbon_text_en"],
            hi=v["dr_ribbon_text_hi"],
            link_en=v["dr_ribbon_link_text_en"],
            link_hi=v["dr_ribbon_link_text_hi"],
        )
    else:
        repl["DR_RIBBON_BLOCK"] = ""

    # Footer mirror block
    if v["footer_mirror_block"] == "main_points_to_mirror":
        repl["FOOTER_MIRROR_BLOCK"] = FOOTER_MAIN_POINTS_TO_MIRROR
    else:
        repl["FOOTER_MIRROR_BLOCK"] = FOOTER_MIRROR_POINTS_TO_MAIN

    out = template
    for key, val in repl.items():
        out = out.replace("{{" + key + "}}", val)
    return out


def render_js(template: str, v: dict) -> str:
    """Render variant-specific JS."""
    # Frame-bust behaviour
    if v["frame_bust_target"] == "self":
        framebust_top = 'window.top.location = location.href;'
        framebust_fallback = '/* cross-origin frame — nothing we can do */'
    else:
        target = v["frame_bust_target"]
        framebust_top = f'window.top.location = "{target}";'
        framebust_fallback = f'window.location = "{target}";'

    # MIRROR_URL declaration
    if v.get("mirror_url_js"):
        mirror_decl = f'const MIRROR_URL = "{v["mirror_url_js"]}";'
    else:
        mirror_decl = '// This variant IS a mirror — failover banner disabled.\nconst MIRROR_URL = null;'

    repl = {
        "FRAMEBUST_TOP":          framebust_top,
        "FRAMEBUST_FALLBACK":     framebust_fallback,
        "MIRROR_URL_DECLARATION": mirror_decl,
        "FP_SUFFIX":              v.get("fingerprint_suffix", ""),
    }
    out = template
    for key, val in repl.items():
        out = out.replace("{{" + key + "}}", val)
    return out


def build_variant(name: str, v: dict, template_html: str, template_js: str, css: str) -> None:
    """Emit one fully-built static site to _build/<name>/."""
    out = BUILD_DIR / name
    if out.exists():
        shutil.rmtree(out)
    (out / "css").mkdir(parents=True)
    (out / "js").mkdir()
    (out / "assets").mkdir()

    # HTML
    (out / "index.html").write_text(render_html(template_html, v), encoding="utf-8")
    # CSS — same for everyone
    (out / "css" / "style.css").write_text(css, encoding="utf-8")
    # JS — per-variant
    (out / "js" / "main.js").write_text(render_js(template_js, v), encoding="utf-8")

    # Assets — copy verbatim
    for asset in (ROOT / "assets").iterdir():
        shutil.copy2(asset, out / "assets" / asset.name)

    # humans.txt (copy verbatim from repo if present)
    src_humans = REPO / "humans.txt"
    if src_humans.exists():
        shutil.copy2(src_humans, out / "humans.txt")

    # _redirects (copy verbatim — same for every variant)
    src_redirects = ROOT / "_redirects"
    if src_redirects.exists():
        shutil.copy2(src_redirects, out / "_redirects")

    # ── render _headers per variant ─────────────────────────────────────
    headers_tpl = (ROOT / "_headers.template").read_text(encoding="utf-8")
    headers_out = (headers_tpl
                   .replace("{{CSP_CONNECT_SRC}}", v["csp_connect_src"])
                   .replace("{{ROBOTS}}", v["robots"])
                   .replace("{{FP_SUFFIX}}", v.get("fingerprint_suffix", "")))
    (out / "_headers").write_text(headers_out, encoding="utf-8")

    # ── render manifest.webmanifest per variant ─────────────────────────
    manifest_tpl = (ROOT / "manifest.template.webmanifest").read_text(encoding="utf-8")
    manifest_out = (manifest_tpl
                    .replace("{{MANIFEST_NAME}}", v["title"])
                    .replace("{{MANIFEST_ID}}", "/?id=knr-nncc" + v.get("fingerprint_suffix", "")))
    (out / "manifest.webmanifest").write_text(manifest_out, encoding="utf-8")

    # ── render service worker per variant (cache-bust hash) ─────────────
    sw_tpl = (ROOT / "sw.template.js").read_text(encoding="utf-8")
    # cache version = short hash of HTML + CSS + JS — changes whenever content changes
    hash_src = (
        (ROOT / "index.template.html").read_text(encoding="utf-8")
        + (ROOT / "style.css").read_text(encoding="utf-8")
        + (ROOT / "main.js").read_text(encoding="utf-8")
        + json.dumps(v, sort_keys=True)
    )
    cache_version = hashlib.sha256(hash_src.encode("utf-8")).hexdigest()[:10]
    sw_out = sw_tpl.replace("{{CACHE_VERSION}}", cache_version)
    (out / "sw.js").write_text(sw_out, encoding="utf-8")

    # ── render offline.html (same across variants) ──────────────────────
    offline_tpl = (ROOT / "offline.template.html").read_text(encoding="utf-8")
    (out / "offline.html").write_text(offline_tpl, encoding="utf-8")

    # ── render sitemap.xml per variant ──────────────────────────────────
    sitemap_tpl = (ROOT / "sitemap.template.xml").read_text(encoding="utf-8")
    base_url = v.get("base_url", "https://netineticharaiveticharaiveti.in")
    lastmod = datetime.date.today().isoformat()
    sitemap_out = (sitemap_tpl
                   .replace("{{BASE_URL}}", base_url)
                   .replace("{{LASTMOD}}", lastmod))
    (out / "sitemap.xml").write_text(sitemap_out, encoding="utf-8")

    # ── render robots.txt per variant ───────────────────────────────────
    robots_tpl = (ROOT / "robots.template.txt").read_text(encoding="utf-8")
    # If robots is "noindex, follow" we disallow indexing in robots.txt too;
    # if it's "index, follow" we allow.
    if "noindex" in v["robots"]:
        robots_rules = "Disallow: /"
    else:
        robots_rules = "Allow: /"
    robots_out = (robots_tpl
                  .replace("{{BASE_URL}}", base_url)
                  .replace("{{ROBOTS_RULES}}", robots_rules))
    (out / "robots.txt").write_text(robots_out, encoding="utf-8")

    # Ensure .nojekyll exists (so GitHub Pages doesn't run Jekyll)
    (out / ".nojekyll").write_text("", encoding="utf-8")

    print(f"  built _build/{name}/")


def main() -> int:
    config = json.loads((ROOT / "variants.json").read_text(encoding="utf-8"))
    variants = config["variants"]

    # Optional filter from CLI
    only = set()
    if len(sys.argv) > 1 and sys.argv[1] == "--variant":
        only = set(sys.argv[2:])

    template_html = (ROOT / "index.template.html").read_text(encoding="utf-8")
    template_js   = (ROOT / "main.js").read_text(encoding="utf-8")
    css           = (ROOT / "style.css").read_text(encoding="utf-8")

    BUILD_DIR.mkdir(exist_ok=True)
    print(f"building into {BUILD_DIR.relative_to(REPO)}/")
    for name, v in variants.items():
        if only and name not in only:
            continue
        build_variant(name, v, template_html, template_js, css)
    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
