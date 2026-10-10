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
  var ANA_LIGHT = (function () { var l = [0.25, 0.4, -1]; var m = Math.sqrt(l[0]*l[0]+l[1]*l[1]+l[2]*l[2]); return [l[0]/m, l[1]/m, l[2]/m]; })();
  function anaBright(n) { var d = n[0]*ANA_LIGHT[0]+n[1]*ANA_LIGHT[1]+n[2]*ANA_LIGHT[2]; return 0.24 + 0.76 * Math.max(0, d); }
  var ANA_CUBE_C = [[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]];
  var ANA_CUBE_F = [[0,1,2,3],[4,5,6,7],[0,3,7,4],[1,2,6,5],[0,1,5,4],[3,2,6,7]];
  function renderOrbit(scene, angle) {
    var P = scene.params, C = scene.center;
    var cos = Math.cos(angle), sin = Math.sin(angle);
    function rot(p) { var x=p[0]-C[0], y=p[1]-C[1], z=p[2]-C[2]; return [x*cos+z*sin+C[0], y+C[1], -x*sin+z*cos+C[2]]; }
    function proj(p, cam) { var r=rot(p), rz=r[2]-cam[2]; if (rz<=0.02) return null; return [P.CX + P.F*(r[0]-cam[0])/rz*P.S, P.CY - P.F*(r[1]-cam[1])/rz*P.S]; }
    function polyStr(pts) { return '<polygon points="' + pts.map(function(q){ return q[0].toFixed(1)+','+q[1].toFixed(1); }).join(' ') + '"'; }
    function diskSVG(c, r, cam, fill, stroke, sw) { var n=44, pts=[]; for (var i=0;i<n;i++){ var a=i/n*2*Math.PI; var q=proj([c[0]+r*Math.cos(a), c[1]+r*Math.sin(a), c[2]], cam); if(!q) return ''; pts.push(q); } return polyStr(pts)+' fill="'+fill+'"'+(stroke?' stroke="'+stroke+'" stroke-width="'+(sw||1.4)+'"':'')+'/>'; }
    function blockSVG(bl, cam, ch) {
      var c=bl.c, w=bl.w||1, h=bl.h||1, d=bl.d||1, base=(bl.br!==undefined?bl.br:0.72);
      var corners=ANA_CUBE_C.map(function(cc){ return [c[0]+cc[0]*w/2, c[1]+cc[1]*h/2, c[2]+cc[2]*d/2]; });
      var rc=corners.map(rot), faces=[];
      ANA_CUBE_F.forEach(function(f){
        var o=f.map(function(idx){ return corners[idx]; });
        var p2=f.map(function(idx){ var p=rc[idx], rz=p[2]-cam[2]; if(rz<=0.02) return null; return [P.CX+P.F*(p[0]-cam[0])/rz*P.S, P.CY-P.F*(p[1]-cam[1])/rz*P.S]; });
        if (!p2.every(Boolean)) return;
        var u=[o[1][0]-o[0][0],o[1][1]-o[0][1],o[1][2]-o[0][2]], v=[o[2][0]-o[0][0],o[2][1]-o[0][1],o[2][2]-o[0][2]];
        var n=[u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]];
        var nl=Math.sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2])||1; n=[n[0]/nl,n[1]/nl,n[2]/nl];
        var fc=[(o[0][0]+o[3][0])/2,(o[0][1]+o[3][1])/2,(o[0][2]+o[3][2])/2];
        if (n[0]*(fc[0]-c[0])+n[1]*(fc[1]-c[1])+n[2]*(fc[2]-c[2]) < 0) n=[-n[0],-n[1],-n[2]];
        faces.push({ depth:(o[0][2]+o[1][2]+o[2][2]+o[3][2])/4, p2:p2, n:[n[0]*cos+n[2]*sin, n[1], -n[0]*sin+n[2]*cos] });
      });
      faces.sort(function(a,b){ return b.depth - a.depth; });
      return faces.map(function(fa){ var br=anaBright(fa.n)*base; return polyStr(fa.p2)+' fill="'+orbitFill(ch,br)+'" stroke="'+orbitFill(ch,br*0.35)+'" stroke-width="1.1"/>'; }).join('');
    }
    function prismSVG(pr, cam, ch) {
      var H = pr.height, R = pr.r, hx = pr.hx, hz = pr.hz, out = [];
      var faces = [];
      (pr.faces || []).forEach(function(f){
        var n, u, v, lp;
        if (f.top) {                                  // bovenvlak: polygon van hoeken
          n = [0, 1, 0]; u = [1, 0, 0]; v = [0, 0, 1];
          lp = f.ang.map(function(a){ a = a * Math.PI / 180; return [R * Math.cos(a), H, R * Math.sin(a)]; });
        } else if (f.q) {                             // expliciete quad in world-units (gestapelde lagen)
          n = f.n; u = f.u; v = f.v;
          lp = f.q.map(function(p){ return [p[0], p[1], p[2]]; });
        } else if (f.a0 !== undefined) {              // prisma-vlak: twee hoeken (graden) in de doorsnede
          var a0 = f.a0 * Math.PI / 180, a1 = f.a1 * Math.PI / 180, mid = (a0 + a1) / 2;
          n = [Math.cos(mid), 0, Math.sin(mid)];
          u = [-Math.sin(mid), 0, Math.cos(mid)];     // lees-richting over het vlak
          v = [0, -1, 0];                             // lees-omlaag op het vlak
          lp = [[R*Math.cos(a0), 0, R*Math.sin(a0)], [R*Math.cos(a1), 0, R*Math.sin(a1)],
                [R*Math.cos(a1), H, R*Math.sin(a1)], [R*Math.cos(a0), H, R*Math.sin(a0)]];
        } else {                                      // rechthoekig prisma via hx/hz
          n = f.n; u = f.u; v = f.v;
          lp = f.pts.map(function(p){ return [p[0]*hx, p[1]*H, p[2]*hz]; });
        }
        lp = lp.map(function(p){ return [pr.c[0]+p[0], pr.c[1]+p[1], pr.c[2]+p[2]]; });
        var rp = lp.map(rot);
        var p2 = rp.map(function(p){ var rz=p[2]-cam[2]; if(rz<=0.02) return null; return [P.CX+P.F*(p[0]-cam[0])/rz*P.S, P.CY-P.F*(p[1]-cam[1])/rz*P.S]; });
        if (!p2.every(Boolean)) return;
        var fc = [0,0,0]; rp.forEach(function(p){ fc[0]+=p[0]; fc[1]+=p[1]; fc[2]+=p[2]; });
        fc = [fc[0]/lp.length, fc[1]/lp.length, fc[2]/lp.length];
        var nr = [n[0]*cos+n[2]*sin, n[1], -n[0]*sin+n[2]*cos];
        // zichtbaar als de camera aan de buitenkant van het vlak staat: dot(n, cam - fc) > 0
        if (nr[0]*(cam[0]-fc[0])+nr[1]*(cam[1]-fc[1])+nr[2]*(cam[2]-fc[2]) <= 0) return;
        var br = anaBright(nr) * (f.br !== undefined ? f.br : 0.62);
        faces.push({ depth: fc[2], poly: polyStr(p2), fill: orbitFill(ch, br),
                     fc: fc, u: u, v: v, lines: f.lines || [], br: br });
      });
      faces.sort(function(a,b){ return b.depth - a.depth; });
      faces.forEach(function(fa){
        out.push(fa.poly + ' fill="' + fa.fill + '" stroke="' + orbitFill(ch, fa.br*0.35) + '" stroke-width="1.2"/>');
        var O = [P.CX + P.F*(fa.fc[0]-cam[0])/fa.fc[2]*P.S, P.CY - P.F*(fa.fc[1]-cam[1])/fa.fc[2]*P.S];
        // lineaire deel van de projectie: scherm-richting van een as in het vlak (zonder diepte-stap)
        function basis(ax){ var r=[ax[0]*cos+ax[2]*sin, ax[1], -ax[0]*sin+ax[2]*cos]; return [r[0], -r[1]]; }
        var U = basis(fa.u), V = basis(fa.v);
        var t = '<g transform="matrix(' + U[0].toFixed(4) + ',' + U[1].toFixed(4) + ',' + V[0].toFixed(4) + ',' + V[1].toFixed(4) + ',' + O[0].toFixed(1) + ',' + O[1].toFixed(1) + ')">';
        fa.lines.forEach(function(l){ t += '<text x="0" y="' + l.dy + '" text-anchor="middle" font-size="' + (l.fs||13) + '" fill="' + orbitFill(ch, Math.max(0.85, fa.br)) + '">' + l.t + '</text>'; });
        out.push(t + '</g>');
      });
      return out.join('');
    }
    function renderCam(cam, ch) {
      var o=[];
      (scene.disks||[]).forEach(function(dk){ o.push(diskSVG(dk.c, dk.r, cam, orbitFill(ch, dk.br!==undefined?dk.br:0.4), orbitFill(ch,0.95), 1.5)); });
      (scene.lines || scene.axes || []).forEach(function(ax){ var a=proj(ax.a,cam), b=proj(ax.b,cam); if(a&&b) o.push('<line x1="'+a[0].toFixed(1)+'" y1="'+a[1].toFixed(1)+'" x2="'+b[0].toFixed(1)+'" y2="'+b[1].toFixed(1)+'" stroke="'+orbitFill(ch, ax.br!==undefined?ax.br:0.65)+'" stroke-width="'+(ax.w||1.5)+'"'+(ax.dash?' stroke-dasharray="'+ax.dash+'"':'')+'/>'); });
      (scene.blocks||[]).forEach(function(bl){ o.push(blockSVG(bl, cam, ch)); });
      if (scene.prism) o.push(prismSVG(scene.prism, cam, ch));
      var EX = scene.pointScale || 1.6;   // hoe sterk het formaat met diepte meegaat (1 = puur perspectief)
      (scene.points||[]).forEach(function(pt){ var r=rot(pt.p), rz=r[2]-cam[2]; if(rz<=0.02) return;
        var sc=Math.pow((C[2]-cam[2])/rz, EX), q=[P.CX+P.F*(r[0]-cam[0])/rz*P.S, P.CY-P.F*(r[1]-cam[1])/rz*P.S];
        var base=pt.mine?8:(pt.hot?7:4.5), rad=base*sc;
        o.push('<circle cx="'+q[0].toFixed(1)+'" cy="'+q[1].toFixed(1)+'" r="'+rad.toFixed(2)+'" fill="'+orbitFill(ch, pt.mine?1:(pt.hot?0.9:0.72))+'"'+(pt.mine?' stroke="'+orbitFill(ch,0.35)+'" stroke-width="'+(1.6*sc).toFixed(2)+'"':'')+'/>'); });
      if (scene.origin) { var or=rot(scene.origin), orz=or[2]-cam[2]; if(orz>0.02) { var osc=Math.pow((C[2]-cam[2])/orz, EX); var op=[P.CX+P.F*(or[0]-cam[0])/orz*P.S, P.CY-P.F*(or[1]-cam[1])/orz*P.S]; o.push('<circle cx="'+op[0].toFixed(1)+'" cy="'+op[1].toFixed(1)+'" r="'+(3*osc).toFixed(2)+'" fill="'+orbitFill(ch,1)+'"/>'); } }
      return o.join('');
    }
    // vlakke 2D-labels: draait MEE met de scène, maar zonder rood/cyaan-offset (blijft leesbaar)
    function projC(p) { var r=rot(p), rz=r[2]; if (rz<=0.02) return null; return [P.CX + P.F*(r[0])/rz*P.S, P.CY - P.F*(r[1]-P.camL[1])/rz*P.S]; }
    var labels='';
    function addLbl(p, t, dx, dy, anchor, cls, fs) { if (!t) return; var q=projC(p); if(!q) return; labels += '<text x="'+(q[0]+(dx||0)).toFixed(1)+'" y="'+(q[1]+(dy!==undefined?dy:-12)).toFixed(1)+'" class="'+(cls||'lbl-dim')+'" font-size="'+(fs||11)+'" text-anchor="'+(anchor||'middle')+'">'+t+'</text>'; }
    (scene.points||[]).forEach(function(lp){ addLbl(lp.p, lp.label, lp.ldx, lp.ldy, lp.anchor, lp.mine?'lbl-mine':(lp.hot?'lbl-accent':'lbl-dim')); });
    (scene.blocks||[]).forEach(function(bl){ if (bl.label) addLbl([bl.c[0], bl.c[1]+(bl.h||1)/2+0.16, bl.c[2]], bl.label, bl.ldx||0, bl.ldy!==undefined?bl.ldy:4, 'middle', bl.hot?'lbl-accent':'lbl-dim'); });
    (scene.endLabels||[]).forEach(function(el){ addLbl(el.p, el.t, el.dx, el.dy, el.anchor, 'lbl-dim', 12); });
    if (scene.originLabel) addLbl(scene.origin, scene.originLabel, 0, -16, 'middle', 'lbl-accent', 12);
    (scene.labels||[]).forEach(function(l){ addLbl(l.p, l.t, l.dx, l.dy, l.anchor, l.cls, l.fs); });
    var red = renderCam(P.camL, 'red'), cyan = renderCam(P.camR, 'cyan');
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
