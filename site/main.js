/* TRENDREIS — main.js (multi-page) */
(function () {
  "use strict";
  var root = document.documentElement;

  /* ---------------------------------------------------------- theme */
  var themeBtn = document.getElementById("themeBtn");
  function setTheme(t) {
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("trendreis.theme", t); } catch (e) {}
    if (themeBtn) themeBtn.textContent = (t === "light" ? "DARK" : "LIGHT");
  }
  var savedTheme = null;
  try { savedTheme = localStorage.getItem("trendreis.theme"); } catch (e) {}
  if (savedTheme) setTheme(savedTheme);
  if (themeBtn) themeBtn.addEventListener("click", function () {
    setTheme(root.getAttribute("data-theme") === "light" ? "dark" : "light");
  });

  /* ---------------------------------------------------------- 3D + depth */
  var d3Btn = document.getElementById("d3Btn");
  var depthRange = document.getElementById("depthRange");
  var depthNum = document.getElementById("depthNum");
  var sb3d = document.getElementById("sb3d");
  var FACTORS = { far: 0.25, mid: 0.6, near: 1.0 };

  function applyParallax(depth) {
    var chC = document.getElementById("chC");
    if (!chC) return;
    ["far", "mid", "near"].forEach(function (layer) {
      var el = chC.querySelector(".layer-" + layer);
      if (el) el.style.transform = "translate(" + (depth * FACTORS[layer]) + "px,0)";
    });
  }
  function set3D(on) {
    document.body.setAttribute("data-3d", on ? "on" : "off");
    if (d3Btn) d3Btn.setAttribute("aria-pressed", on ? "true" : "false");
    if (sb3d) sb3d.textContent = on ? "AAN" : "UIT";
    try { localStorage.setItem("trendreis.3d", on ? "on" : "off"); } catch (e) {}
    if (on && depthRange) applyParallax(parseInt(depthRange.value, 10) || 0);
  }
  var saved3d = null;
  try { saved3d = localStorage.getItem("trendreis.3d"); } catch (e) {}
  if (d3Btn) d3Btn.addEventListener("click", function () {
    set3D(document.body.getAttribute("data-3d") === "on" ? false : true);
  });
  if (depthRange) {
    depthRange.addEventListener("input", function () {
      if (depthNum) depthNum.textContent = depthRange.value + "px";
      if (document.body.getAttribute("data-3d") === "on") applyParallax(parseInt(depthRange.value, 10) || 0);
    });
  }
  // init
  if (depthNum && depthRange) depthNum.textContent = depthRange.value + "px";
  set3D(saved3d !== "off");

  /* ---------------------------------------------------------- mobile menu */
  var burger = document.getElementById("burger");
  if (burger) burger.addEventListener("click", function () {
    document.body.classList.toggle("nav-open");
  });
  var scrim = document.getElementById("scrim");
  if (scrim) scrim.addEventListener("click", function () {
    document.body.classList.remove("nav-open");
  });

  /* ---------------------------------------------------------- materiaal highlights */
  function pulse(id) {
    var el = document.getElementById("hl-" + id);
    if (!el) return;
    el.classList.remove("pulse");
    // force reflow to restart animation
    void el.offsetWidth;
    el.classList.add("pulse");
    el.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  function handleHlParam() {
    var m = location.search.match(/[?&]hl=([A-Za-z0-9_-]+)/);
    if (m) setTimeout(function () { pulse(m[1]); }, 260);
  }
  if (document.body.getAttribute("data-page") === "materiaal") {
    handleHlParam();
    // legend + any .hlbox click → pulse
    document.addEventListener("click", function (e) {
      var leg = e.target.closest("[data-hl]");
      if (leg) { e.preventDefault(); pulse(leg.getAttribute("data-hl")); return; }
      var box = e.target.closest(".hlbox");
      if (box) pulse(box.getAttribute("data-id"));
    });
  }

  /* ---------------------------------------------------------- TOC scroll-spy */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
  if (tocLinks.length > 1 && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) {
      var id = a.getAttribute("href").slice(1);
      var el = document.getElementById(id);
      if (el) map[id] = a;
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          tocLinks.forEach(function (a) { a.style.color = ""; });
          var a = map[en.target.id];
          if (a) a.style.color = "var(--accent)";
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(map).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) io.observe(el);
    });
  }
})();
