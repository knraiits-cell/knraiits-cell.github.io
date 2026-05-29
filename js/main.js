// ─────────────────────────────────────────────────────────────
// netineti charaiveti charaiveti — site script
// ─────────────────────────────────────────────────────────────

/* ─── Anti-clone & integrity guard ──────────────────────────────────
   Browser-side checks; not a substitute for HTTP security headers but they
   make casual cloning noisy and traceable.
     1. Frame-bust any iframe (clickjacking defence).
     2. Detect unexpected host and warn.
     3. Console fingerprint to help identify clones.
─────────────────────────────────────────────────────────────────────── */
(function antiClone() {
  try {
    if (window.top !== window.self) {
      window.top.location = "https://netineticharaiveticharaiveti.in/";
    }
  } catch (e) {
    window.location = "https://netineticharaiveticharaiveti.in/";
  }

  const allowedHosts = [
    "netineticharaiveticharaiveti.in",
    "www.netineticharaiveticharaiveti.in",
    "localhost",
    "127.0.0.1",
    "",
    "sites.pplx.app",
    "www.perplexity.ai",
    "knraiits-cell.github.io",
    "github.io",
  ];
  const host = (location.hostname || "").toLowerCase();
  const isAllowed = allowedHosts.some(
    (h) => host === h || (h && host.endsWith("." + h))
  );
  if (!isAllowed) {
    document.documentElement.setAttribute("data-cloned", "true");
    try {
      const banner = document.createElement("div");
      banner.setAttribute("role", "alert");
      banner.style.cssText = [
        "position:fixed", "inset:0 0 auto 0", "z-index:99999",
        "padding:14px 18px", "background:#220011", "color:#ffd6e6",
        "font:14px/1.5 system-ui, sans-serif", "text-align:center",
        "border-bottom:1px solid #ff6a9b"
      ].join(";");
      banner.innerHTML =
        "⚠️ This appears to be a clone. The authentic site is " +
        '<a href="https://netineticharaiveticharaiveti.in/" ' +
        'style="color:#ff9bbd;text-decoration:underline">' +
        "netineticharaiveticharaiveti.in</a>. " +
        "Please report clones to knraiits@gmail.com.";
      document.addEventListener("DOMContentLoaded", () =>
        document.body && document.body.prepend(banner)
      );
    } catch (e) { /* no-op */ }
  }

  try {
    const css1 = "color:#eb9cff;font:600 14px/1.4 sans-serif";
    const css2 = "color:#f3c2f3;font:12px/1.4 sans-serif";
    console.log("%c netineti charaiveti charaiveti ", css1);
    console.log(
      "%c© Krishna Nand Rai · K.N. Rai · Khalil Asgar (ख़लील अस्गर)\n" +
      "canonical: https://netineticharaiveticharaiveti.in/\n" +
      "fingerprint: KNR-NNCC-IN-2025-Q2\n" +
      "served from: " + host,
      css2
    );
    console.log(
      "%cIf you see this notice on a site that is NOT netineticharaiveticharaiveti.in, you are looking at a clone. Please report to knraiits@gmail.com.",
      "color:#ff9bbd;font:12px/1.4 sans-serif"
    );
  } catch (e) { /* no-op */ }
})();

/* ─── Mirror / fallback fail-over ────────────────────────────────
   If the main site is broken (critical assets failed to load, repeated
   network errors, or stylesheet missing), surface a banner offering the
   pplx.app DR mirror at knraiits-cell.github.io/netineti-mirror.
   We do NOT auto-redirect — we let the visitor choose. Surprise redirects
   are hostile UX; one-tap fail-over is the right balance.
─────────────────────────────────────────────────────────────────────── */
const MIRROR_URL = "https://knraiits-cell.github.io/netineti-mirror";

(function mirrorFailover() {
  let shown = false;
  let assetErrors = 0;

  function showMirrorBanner(reason) {
    if (shown) return;
    shown = true;
    const isHi = document.documentElement.getAttribute("data-lang") === "hi";
    const msg = isHi
      ? "इस पार्ष्व पर कुछ चित्र शायद पूरा न खुले। वैकल्पिक स्थल पर जाएँ?"
      : "Some parts of this page may not be loading correctly. Try the mirror site?";
    const cta = isHi ? "वैकल्पिक स्थल खोलें" : "Open mirror site";
    const dismiss = isHi ? "बंद करें" : "Dismiss";

    const bar = document.createElement("div");
    bar.setAttribute("role", "alert");
    bar.setAttribute("data-reason", reason);
    bar.style.cssText = [
      "position:fixed", "left:0", "right:0", "bottom:0", "z-index:99998",
      "padding:12px 16px", "background:#14134d", "color:#f3c2f3",
      "font:14px/1.5 system-ui, sans-serif", "text-align:center",
      "border-top:1px solid rgba(243,194,243,0.28)",
      "box-shadow:0 -8px 24px -12px rgba(0,0,0,0.6)"
    ].join(";");
    bar.innerHTML =
      "<span style='margin-right:14px'>" + msg + "</span>" +
      "<a href='" + MIRROR_URL + "' target='_blank' rel='noopener' " +
      "style='color:#eb9cff;text-decoration:underline;margin-right:14px'>" +
      cta + "</a>" +
      "<button type='button' style='background:transparent;border:1px solid rgba(243,194,243,0.28);color:#f3c2f3;padding:4px 10px;border-radius:999px;cursor:pointer;font:inherit'>" +
      dismiss + "</button>";
    bar.querySelector("button").addEventListener("click", () => bar.remove());
    (document.body || document.documentElement).appendChild(bar);
  }

  // 1. Watch for critical asset load failures.
  window.addEventListener("error", (e) => {
    const t = e.target;
    if (!t || t === window) return;
    if (t.tagName === "LINK" || t.tagName === "SCRIPT" || t.tagName === "IMG") {
      assetErrors++;
      // Two or more failed critical assets → surface mirror.
      if (assetErrors >= 2) showMirrorBanner("asset-failure");
    }
  }, true);

  // 2. Stylesheet sanity check after load — we look for a CSS custom
  //    property the stylesheet defines on <html>::before. If absent, the
  //    stylesheet failed to load.
  window.addEventListener("load", () => {
    setTimeout(() => {
      try {
        const probe = getComputedStyle(document.documentElement, "::before")
          .getPropertyValue("--css-loaded")
          .trim();
        if (probe !== "1") showMirrorBanner("stylesheet-missing");
      } catch (e) { /* no-op */ }
    }, 1200);
  });
})();

// Footer year
document.getElementById("yr").textContent = new Date().getFullYear();

/* ─── Bilingual toggle ─────────────────────────────────────── */
const LANG_KEY = "knrai.lang";
const VALID = new Set(["en", "hi"]);

function detectInitialLang() {
  const saved = localStorage.getItem(LANG_KEY);
  if (saved && VALID.has(saved)) return saved;
  const browser = (navigator.language || "en").toLowerCase();
  if (browser.startsWith("hi")) return "hi";
  return "en";
}

function applyLang(lang) {
  if (!VALID.has(lang)) lang = "en";

  // Update root attributes — drives CSS font selection
  const html = document.documentElement;
  html.setAttribute("data-lang", lang);
  html.setAttribute("lang", lang === "hi" ? "hi" : "en");

  // Swap content for every element with both data-en / data-hi
  document.querySelectorAll("[data-en][data-hi]").forEach((el) => {
    const val = el.getAttribute(lang === "hi" ? "data-hi" : "data-en");
    if (val == null) return;
    // Use innerHTML so we keep inline <em>, <strong>, <a> formatting
    if (el.innerHTML !== val) el.innerHTML = val;
  });

  // Update toggle UI
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    const active = btn.dataset.setLang === lang;
    btn.classList.toggle("is-active", active);
    btn.setAttribute("aria-pressed", String(active));
  });

  localStorage.setItem(LANG_KEY, lang);
}

document.querySelectorAll(".lang-btn").forEach((btn) => {
  btn.addEventListener("click", () => applyLang(btn.dataset.setLang));
});

// Initial application
applyLang(detectInitialLang());

/* ─── Reveal-on-scroll ─────────────────────────────────────── */
const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const targets = document.querySelectorAll(".section, .hero-portrait, .hero-text");

if (!prefersReduced && "IntersectionObserver" in window) {
  targets.forEach((el) => el.classList.add("reveal"));
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.05, rootMargin: "0px 0px -2% 0px" }
  );
  targets.forEach((el) => io.observe(el));

  // Safety net
  setTimeout(() => {
    document.querySelectorAll(".reveal:not(.in)").forEach((el) => el.classList.add("in"));
  }, 1500);
}

/* ─── Header subtle shadow on scroll ───────────────────────── */
const header = document.querySelector(".site-header");
const onScroll = () => {
  if (window.scrollY > 12) header.style.boxShadow = "0 8px 24px -16px rgba(0,0,0,0.6)";
  else header.style.boxShadow = "none";
};
document.addEventListener("scroll", onScroll, { passive: true });
onScroll();
