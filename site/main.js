/* TRENDREIS — interactiviteit (orange console)
   - theme toggle (dark default / light)
   - 3D-anaglyph toggle + depth-slider
   - nav scroll-spy
   Alles respectueert prefers-reduced-motion en staat lokaal (geen backend). */
(function () {
  "use strict";
  const root = document.documentElement;
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));

  // ---------- theme ----------
  const THEME_KEY = "trendreis.theme";
  function setTheme(t) {
    if (t === "light") root.setAttribute("data-theme", "light");
    else root.removeAttribute("data-theme");
    try { localStorage.setItem(THEME_KEY, t); } catch (e) {}
    syncThemeBtn();
  }
  function syncThemeBtn() {
    const btn = $("#themeBtn");
    if (!btn) return;
    const light = root.getAttribute("data-theme") === "light";
    btn.textContent = light ? "DARK" : "LIGHT";
    btn.setAttribute("aria-pressed", String(light === false));
  }

  // ---------- 3D / depth ----------
  const D3_KEY = "trendreis.3d";
  const DP_KEY = "trendreis.depth";
  const DEF_DEPTH = 10; // px
  let depth = DEF_DEPTH;
  function set3d(on) {
    root.setAttribute("data-3d", on ? "on" : "off");
    try { localStorage.setItem(D3_KEY, on ? "on" : "off"); } catch (e) {}
    sync3dBtn();
    if (typeof applyParallax === "function") applyParallax(on ? depth : 0);
  }
  // parallax-factoren per dieptelaag (near = 1.0, mid, far)
  const LAYER = { far: 0.25, mid: 0.6, near: 1.0 };

  function sync3dBtn() {
    const btn = $("#d3Btn");
    if (!btn) return;
    const on = root.getAttribute("data-3d") === "on";
    btn.classList.toggle("on", on);
    btn.setAttribute("aria-pressed", String(on));
    const wrap = $("#depthWrap");
    if (wrap) wrap.style.opacity = on ? "1" : "0.4";
    const sb = $("#sb3d");
    if (sb) sb.textContent = on ? "AAN" : "UIT";
  }

  function applyParallax(depth) {
    const chC = document.getElementById("chC");
    if (!chC) return;
    for (const name of Object.keys(LAYER)) {
      const g = chC.querySelector(".layer-" + name);
      if (!g) continue;
      const off = (depth * LAYER[name]).toFixed(2);
      g.setAttribute("transform", `translate(${off},0)`);
    }
  }

  function setDepth(px) {
    px = Math.max(0, Math.min(30, Number(px) || 0));
    depth = px;
    applyParallax(px);
    const n = $("#depthNum");
    if (n) n.textContent = px + "px";
    try { localStorage.setItem(DP_KEY, String(px)); } catch (e) {}
  }

  // ---------- nav scroll-spy ----------
  function spy() {
    const links = $$(".nav a[data-sec]");
    if (!links.length) return;
    const y = window.scrollY + 120;
    let cur = links[0].getAttribute("data-sec");
    for (const a of links) {
      const el = document.getElementById(a.getAttribute("data-sec"));
      if (el && el.offsetTop <= y) cur = a.getAttribute("data-sec");
    }
    links.forEach((a) => a.classList.toggle("cur", a.getAttribute("data-sec") === cur));
  }

  // ---------- init ----------
  function init() {
    // theme
    let savedTheme = null;
    try { savedTheme = localStorage.getItem(THEME_KEY); } catch (e) {}
    setTheme(savedTheme === "light" ? "light" : "dark");
    const tb = $("#themeBtn");
    if (tb) tb.addEventListener("click", () => {
      const light = root.getAttribute("data-theme") === "light";
      setTheme(light ? "dark" : "light");
    });

    // 3d
    let saved3d = null;
    try { saved3d = localStorage.getItem(D3_KEY); } catch (e) {}
    set3d(saved3d === "off" ? false : true); // default aan (het is de signatuur)
    const d3 = $("#d3Btn");
    if (d3) d3.addEventListener("click", () => {
      set3d(root.getAttribute("data-3d") !== "on");
    });

    // depth
    let savedDepth = null;
    try { savedDepth = localStorage.getItem(DP_KEY); } catch (e) {}
    const d = savedDepth !== null ? Number(savedDepth) : DEF_DEPTH;
    setDepth(d);
    const range = $("#depthRange");
    if (range) {
      range.value = d;
      range.addEventListener("input", () => setDepth(range.value));
    }

    // nav spy
    let t = null;
    window.addEventListener("scroll", () => {
      if (t) return;
      t = requestAnimationFrame(() => { spy(); t = null; });
    }, { passive: true });
    spy();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
