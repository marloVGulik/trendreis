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

  /* ---------------------------------------------------------- 3D (twee-camera anaglyph) */
  // De paralaxe zit nu IN de SVG (twee camera's, links=rood/rechts=cyaan). De 3D-knop
  // schakelt alleen tussen anaglyph (rood+cyaan) en platte 2D (alleen rood) in.
  var d3Btn = document.getElementById("d3Btn");
  var sb3d = document.getElementById("sb3d");
  function set3D(on) {
    document.body.setAttribute("data-3d", on ? "on" : "off");
    if (d3Btn) d3Btn.setAttribute("aria-pressed", on ? "true" : "false");
    if (sb3d) sb3d.textContent = on ? "AAN" : "UIT";
    try { localStorage.setItem("trendreis.3d", on ? "on" : "off"); } catch (e) {}
  }
  var saved3d = null;
  try { saved3d = localStorage.getItem("trendreis.3d"); } catch (e) {}
  if (d3Btn) d3Btn.addEventListener("click", function () {
    set3D(document.body.getAttribute("data-3d") === "on" ? false : true);
  });
  set3D(saved3d !== "off");

  /* ---------------------------------------------------------- orbit anaglyph (interactief 3D) */
  // Scène-data uit data-scene (JSON). Projecteert vanuit twee camera's (links=rood, rechts=cyaan).
  // Muis-sleep (of touch) draait de scène rond de y-as => camera draait eromheen.
  function orbitFill(channel, b) {
    b = Math.max(0, Math.min(1, b));
    if (channel === 'red') return 'rgb(' + Math.round(255*b) + ',' + Math.round(16*b) + ',' + Math.round(16*b) + ')';
    return 'rgb(0,' + Math.round(229*b) + ',' + Math.round(229*b) + ')';
  }
  function renderOrbit(scene, angle) {
    var P = scene.params, C = scene.center;
    var cos = Math.cos(angle), sin = Math.sin(angle);
    function rot(p) {
      var x = p[0]-C[0], y = p[1]-C[1], z = p[2]-C[2];
      return [x*cos + z*sin + C[0], y + C[1], -x*sin + z*cos + C[2]];
    }
    function proj(p, cam) {
      var r = rot(p), rz = r[2]-cam[2];
      if (rz <= 0.02) return null;
      return [P.CX + P.F*(r[0]-cam[0])/rz*P.S, P.CY - P.F*(r[1]-cam[1])/rz*P.S];
    }
    function renderCam(cam, channel) {
      var o = [], col = orbitFill(channel, 0.8);
      var op = proj(scene.origin, cam);
      if (op) o.push('<circle cx="'+op[0].toFixed(1)+'" cy="'+op[1].toFixed(1)+'" r="3" fill="'+orbitFill(channel,1)+'"/>');
      for (var i=0;i<scene.axes.length;i++) {
        var ax = scene.axes[i], a = proj(ax.a, cam), b = proj(ax.b, cam);
        if (a && b) o.push('<line x1="'+a[0].toFixed(1)+'" y1="'+a[1].toFixed(1)+'" x2="'+b[0].toFixed(1)+'" y2="'+b[1].toFixed(1)+'" stroke="'+col+'" stroke-width="'+ax.w+'"'+(ax.dash?' stroke-dasharray="'+ax.dash+'"':'')+'/');
      }
      for (var j=0;j<scene.points.length;j++) {
        var pt = scene.points[j], q = proj(pt.p, cam);
        if (q) o.push('<circle cx="'+q[0].toFixed(1)+'" cy="'+q[1].toFixed(1)+'" r="'+(pt.hot?7:4.5)+'" fill="'+orbitFill(channel, pt.hot?1:0.72)+'"/>');
      }
      return o.join('');
    }
    var red = renderCam(P.camL, 'red'), cyan = renderCam(P.camR, 'cyan');
    var cCam = [0, P.camL[1], 0], labels = '';
    for (var k=0;k<scene.points.length;k++) {
      var lp = scene.points[k], c = proj(lp.p, cCam);
      if (c) labels += '<text x="'+(c[0]+(lp.ldx||0)).toFixed(1)+'" y="'+(c[1]+(lp.ldy!==undefined?lp.ldy:-12)).toFixed(1)+'" class="'+(lp.hot?'lbl-accent':'lbl-dim')+'" font-size="11" text-anchor="'+(lp.anchor||'middle')+'">'+lp.label+'</text>';
    }
    for (var m=0;m<scene.endLabels.length;m++) {
      var el = scene.endLabels[m], e = proj(el.p, cCam);
      if (e) labels += '<text x="'+(e[0]+el.dx).toFixed(1)+'" y="'+(e[1]+el.dy).toFixed(1)+'" class="lbl-dim" font-size="12" text-anchor="'+el.anchor+'">'+el.t+'</text>';
    }
    return '<svg class="anaglyph" viewBox="'+P.viewBox+'" preserveAspectRatio="xMidYMid meet" role="img">\n'
         + '<g id="chR" class="chR">'+red+'</g>\n'
         + '<g id="chC" class="chC">'+cyan+'</g>\n'
         + '<g class="anaglyph-labels">'+labels+'</g>\n</svg>';
  }
  try {
  document.querySelectorAll('.anaglyph-orbit').forEach(function (div) {
    if (div.__orbitInit) return;
    div.__orbitInit = true;
    var scene = JSON.parse(div.getAttribute('data-scene'));
    var hint = div.querySelector('.orbit-hint');
    var host = document.createElement('div');
    host.className = 'orbit-svg';
    div.insertBefore(host, hint);
    var angle = 0;
    function paint() { host.innerHTML = renderOrbit(scene, angle); }
    paint();
    var dragging = false, lastX = 0;
    function px(e) { return e.touches ? e.touches[0].clientX : e.clientX; }
    function down(e) { dragging = true; lastX = px(e); if (hint) hint.style.opacity = '0'; e.preventDefault(); }
    function move(e) { if (!dragging) return; var x = px(e); angle += (x - lastX) * 0.008; lastX = x; paint(); }
    function up() { dragging = false; }
    div.addEventListener('mousedown', down);
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    div.addEventListener('touchstart', down, { passive: false });
    div.addEventListener('touchmove', move, { passive: false });
    window.addEventListener('touchend', up);
  });
  } catch (e) { window.__orbitErr = String(e) + ' | ' + (e.stack || '').split('\n').slice(0,3).join(' // '); }

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
    // legend-klik → scroll + pulse (box zelf opent de lightbox via .nb-img)
    document.addEventListener("click", function (e) {
      var leg = e.target.closest("[data-hl]");
      if (leg) { e.preventDefault(); pulse(leg.getAttribute("data-hl")); }
    });
  }

  /* ---------------------------------------------------------- lightbox (foto's groter) */
  var lightbox = document.getElementById("lightbox");
  var lbWrap = lightbox ? lightbox.querySelector(".lb-imgwrap") : null;
  var lbTitle = lightbox ? lightbox.querySelector(".lb-title") : null;
  function openLightbox(src, name, boxesHtml) {
    if (!lightbox || !lbWrap) return;
    lbWrap.innerHTML = '<img src="' + src + '" alt="' + name + '">' + (boxesHtml || "");
    if (lbTitle) lbTitle.textContent = name;
    lightbox.hidden = false;
    document.body.style.overflow = "hidden";
  }
  function closeLightbox() {
    if (!lightbox) return;
    lightbox.hidden = true;
    if (lbWrap) lbWrap.innerHTML = "";
    document.body.style.overflow = "";
  }
  if (lightbox) {
    var lbClose = lightbox.querySelector(".lb-close");
    if (lbClose) lbClose.addEventListener("click", closeLightbox);
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox || e.target.classList.contains("lb-stage")) closeLightbox();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !lightbox.hidden) closeLightbox(); });
    // notebook-foto's (eventuele bron-quote-boxen komen mee)
    Array.prototype.slice.call(document.querySelectorAll(".nb-img")).forEach(function (wrap) {
      wrap.style.cursor = "zoom-in";
      wrap.addEventListener("click", function () {
        var img = wrap.querySelector("img");
        if (!img) return;
        var boxes = Array.prototype.map.call(wrap.querySelectorAll(".hlbox"), function (b) { return b.outerHTML; }).join("");
        var name = (img.getAttribute("alt") || "foto").replace(/^Notebook\s*/i, "");
        openLightbox(img.getAttribute("src"), name, boxes);
      });
    });
    // hunter-foto's
    Array.prototype.slice.call(document.querySelectorAll(".phcard img")).forEach(function (img) {
      img.style.cursor = "zoom-in";
      img.addEventListener("click", function () {
        openLightbox(img.getAttribute("src"), img.getAttribute("alt") || "foto", "");
      });
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
