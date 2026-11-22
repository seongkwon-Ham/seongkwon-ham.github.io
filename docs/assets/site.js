/* Shared behavior for every page: theme toggle, sticky nav, scroll reveal,
   and the paper figures (only on pages that load figdata.js). */
(function(){
  "use strict";
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var yr = document.getElementById('yr'); if (yr) yr.textContent = new Date().getFullYear();

  /* ---- theme toggle (the saved choice is applied in <head> to avoid a flash) ---- */
  var tb = document.getElementById('themeBtn');
  if (tb) tb.addEventListener('click', function(){
    var dark = getComputedStyle(root).getPropertyValue('--ground').trim().toLowerCase() === '#0d0f13';
    var next = dark ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch(e){}
  });

  /* ---- sticky nav ---- */
  var nav = document.getElementById('nav');
  var onScroll = function(){ nav.classList.toggle('stuck', window.scrollY > 24); };
  onScroll(); window.addEventListener('scroll', onScroll, {passive:true});

  /* ---- scroll reveal (with failsafe) ---- */
  var rv = document.querySelectorAll('.rv');
  var revealAll = function(){ rv.forEach(function(el){ el.classList.add('in'); }); };
  if (reduce || !('IntersectionObserver' in window)) { revealAll(); }
  else {
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){ if (e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
    }, {rootMargin:'0px 0px -8% 0px', threshold:.04});
    rv.forEach(function(el){ io.observe(el); });
    setTimeout(revealAll, 3000);
  }

  /* ---- open the abstract of a paper reached by #anchor ---- */
  function openFromHash(){
    if (!location.hash) return;
    var t = document.getElementById(location.hash.slice(1));
    if (t && t.classList.contains('paper')) { var d = t.querySelector('details'); if (d) d.open = true; t.classList.add('in'); }
  }
  openFromHash(); window.addEventListener('hashchange', openFromHash);

  /* ============================================================
     FIGURES. Drawn from the numbers behind the paper figures
     (assets/figdata.js), so they follow the light/dark tokens.
     ============================================================ */
  var F = window.FIGDATA; if (!F) return;
  function tok(n){ return getComputedStyle(root).getPropertyValue(n).trim(); }
  var MONO = '"IBM Plex Mono", ui-monospace, monospace';

  function niceTicks(lo, hi, n){
    var span = hi - lo, step = Math.pow(10, Math.floor(Math.log10(span / n)));
    var err = span / n / step;
    step *= err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1;
    var t = [], v = Math.ceil(lo / step) * step;
    for (; v <= hi + 1e-9; v += step) t.push(Math.round(v / step) * step);
    return {ticks:t, step:step};
  }
  function fmt(v, step){ var d = step < 1 ? Math.min(2, Math.ceil(-Math.log10(step))) : 0; return v.toFixed(d).replace('-', '−'); }

  function frame(c, spec){
    var ctx = c.ctx, W = c.W, H = c.H;
    var padL = 44, padR = 10, padT = 8, padB = 24;
    var iw = W - padL - padR, ih = H - padT - padB;
    var X = function(x){ return padL + (x - spec.x0) / (spec.x1 - spec.x0) * iw; };
    var Y = function(y){ return padT + (1 - (y - spec.y0) / (spec.y1 - spec.y0)) * ih; };
    ctx.clearRect(0, 0, W, H);
    ctx.font = '500 9.5px ' + MONO; ctx.lineWidth = 1; ctx.textBaseline = 'middle';
    spec.yt.ticks.forEach(function(v){
      var y = Math.round(Y(v)) + .5;
      ctx.strokeStyle = v === 0 ? tok('--ink-3') : tok('--rule-2');
      ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
      ctx.fillStyle = tok('--ink-3'); ctx.textAlign = 'right';
      ctx.fillText(fmt(v, spec.yt.step), padL - 8, y);
    });
    ctx.textAlign = 'center'; ctx.fillStyle = tok('--ink-3');
    var minGap = 34, last = -1e9;
    spec.xt.forEach(function(t){
      var x = X(t.v); if (x - last < minGap) return; last = x;
      ctx.fillText(t.label, x, padT + ih + 14);
      ctx.strokeStyle = tok('--rule'); ctx.beginPath();
      ctx.moveTo(Math.round(x) + .5, padT + ih); ctx.lineTo(Math.round(x) + .5, padT + ih + 4); ctx.stroke();
    });
    ctx.strokeStyle = tok('--rule'); ctx.beginPath(); ctx.moveTo(padL, padT + ih + .5); ctx.lineTo(W - padR, padT + ih + .5); ctx.stroke();
    return {X:X, Y:Y, padL:padL, padT:padT, iw:iw, ih:ih};
  }
  function clip(c, f, p){ c.ctx.save(); c.ctx.beginPath(); c.ctx.rect(0, 0, f.padL + f.iw * p + 6, c.H); c.ctx.clip(); }
  function path(ctx, xs, ys, X, Y){ ctx.beginPath(); xs.forEach(function(x, i){ i ? ctx.lineTo(X(x), Y(ys[i])) : ctx.moveTo(X(x), Y(ys[i])); }); }
  function range(arrs, pad){ var lo = Infinity, hi = -Infinity;
    arrs.forEach(function(a){ a.forEach(function(v){ if (v < lo) lo = v; if (v > hi) hi = v; }); });
    var p = (hi - lo) * (pad || .06); return [lo - p, hi + p]; }
  function axisNote(c, f, txt){
    var ctx = c.ctx; ctx.font = '400 9px ' + MONO; ctx.fillStyle = tok('--ink-3');
    ctx.textAlign = 'right'; ctx.textBaseline = 'top';
    ctx.fillText(txt, f.padL + f.iw, f.padT + 2);
  }

  /* Fig. 1: three lines, markers by significance */
  function drawF1(c, p){
    var S = F.w1, keys = ['Low utilization', 'Median', 'High utilization'];
    var r = range(keys.map(function(k){ return S[k].b; }).concat([[0]]), .08);
    var yt = niceTicks(r[0], r[1], 5);
    var xt = []; for (var h = 0; h <= 18; h += 3) xt.push({v:h, label:String(h)});
    var f = frame(c, {x0:-.4, x1:18.4, y0:r[0], y1:r[1], yt:yt, xt:xt});
    var ctx = c.ctx; clip(c, f, p);
    var sty = {'Low utilization':[tok('--ink-3'), [4,3], 1.3], 'Median':[tok('--ink-2'), [], 1.3], 'High utilization':[tok('--accent'), [], 2]};
    keys.forEach(function(k){
      var s = S[k], st = sty[k];
      ctx.strokeStyle = st[0]; ctx.lineWidth = st[2]; ctx.setLineDash(st[1]);
      path(ctx, s.h, s.b, f.X, f.Y); ctx.stroke(); ctx.setLineDash([]);
      s.h.forEach(function(h, i){
        var x = f.X(h), y = f.Y(s.b[i]);
        ctx.fillStyle = st[0]; ctx.strokeStyle = st[0]; ctx.lineWidth = 1.2;
        if (s.sig[i]) { ctx.beginPath(); ctx.arc(x, y, 2.7, 0, 6.283); ctx.fill(); }
        else { ctx.beginPath(); ctx.moveTo(x-2.4, y-2.4); ctx.lineTo(x+2.4, y+2.4); ctx.moveTo(x+2.4, y-2.4); ctx.lineTo(x-2.4, y+2.4); ctx.stroke(); }
      });
    });
    ctx.restore();
    axisNote(c, f, 'months after the shock');
  }

  /* Fig. 2: cumulative EMI return */
  function drawF2(c, p){
    var S = F.w2, n = S.t.length, idx = S.t.map(function(_, i){ return i; });
    var r = range([S.EMI1, S.EMI3, [0]], .06), yt = niceTicks(r[0], r[1], 5);
    var xt = []; S.t.forEach(function(t, i){ var y = +t.slice(0,4); if (t.slice(5) === '01' && y % 2 === 0) xt.push({v:i, label:String(y)}); });
    var f = frame(c, {x0:0, x1:n - 1, y0:r[0], y1:r[1], yt:yt, xt:xt});
    var ctx = c.ctx; clip(c, f, p);
    ctx.lineWidth = 1.3; ctx.strokeStyle = tok('--ink-2'); ctx.setLineDash([4,3]);
    path(ctx, idx, S.EMI3, f.X, f.Y); ctx.stroke(); ctx.setLineDash([]);
    ctx.lineWidth = 2; ctx.strokeStyle = tok('--accent');
    path(ctx, idx, S.EMI1, f.X, f.Y); ctx.stroke();
    ctx.restore();
    axisNote(c, f, '%');
  }

  /* Fig. 3: event study with band; k = months from Jan 2016 */
  function drawF3(c, p){
    var S = F.w3;
    var r = range([S.lo, S.hi, [0]], .04), yt = niceTicks(r[0], r[1], 5);
    var xt = []; for (var y = 2013; y <= 2024; y++) xt.push({v:(y - 2016) * 12, label:String(y)});
    var f = frame(c, {x0:S.k[0] - 1, x1:S.k[S.k.length - 1] + 1, y0:r[0], y1:r[1], yt:yt, xt:xt});
    var ctx = c.ctx;
    var xe = Math.round(f.X(-.5)) + .5;
    ctx.strokeStyle = tok('--ink-3'); ctx.setLineDash([3,3]); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(xe, f.padT); ctx.lineTo(xe, f.padT + f.ih); ctx.stroke(); ctx.setLineDash([]);
    clip(c, f, p);
    ctx.fillStyle = tok('--band'); ctx.beginPath();
    S.k.forEach(function(k, i){ i ? ctx.lineTo(f.X(k), f.Y(S.hi[i])) : ctx.moveTo(f.X(k), f.Y(S.hi[i])); });
    for (var i = S.k.length - 1; i >= 0; i--) ctx.lineTo(f.X(S.k[i]), f.Y(S.lo[i]));
    ctx.closePath(); ctx.fill();
    ctx.lineWidth = 1.6; ctx.strokeStyle = tok('--accent'); path(ctx, S.k, S.b, f.X, f.Y); ctx.stroke();
    if (S.k.indexOf(-1) >= 0) { ctx.strokeStyle = tok('--ink'); ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(f.X(-1), f.Y(0), 3.6, 0, 6.283); ctx.stroke(); }
    ctx.restore();
    axisNote(c, f, 'log points');
  }

  var charts = [['f1', drawF1], ['f2', drawF2], ['f3', drawF3]].map(function(d){
    var el = document.getElementById(d[0]); if (!el || !el.getContext) return null;
    return {el:el, ctx:el.getContext('2d'), draw:d[1], p: reduce ? 1 : 0, W:0, H:0, started:false};
  }).filter(Boolean);
  if (!charts.length) return;

  function layout(c){
    var r = c.el.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
    c.W = r.width; c.H = r.height;
    c.el.width = Math.round(c.W * dpr); c.el.height = Math.round(c.H * dpr);
    c.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  function render(c){ if (c.W > 20 && c.H > 20) c.draw(c, c.p); }
  function play(c){
    if (c.started) return; c.started = true;
    if (reduce) { c.p = 1; render(c); return; }
    var t0 = null, dur = 1400;
    (function step(ts){ if (t0 === null) t0 = ts;
      var u = Math.min(1, (ts - t0) / dur); c.p = 1 - Math.pow(1 - u, 3); render(c);
      if (u < 1) requestAnimationFrame(step); })(performance.now());
  }
  function all(){ charts.forEach(function(c){ layout(c); render(c); }); }

  all();
  if (!reduce && 'IntersectionObserver' in window) {
    var co = new IntersectionObserver(function(es){
      es.forEach(function(e){ if (!e.isIntersecting) return;
        var c = charts.filter(function(x){ return x.el === e.target; })[0];
        if (c) { setTimeout(function(){ layout(c); play(c); }, 250); co.unobserve(e.target); } });
    }, {threshold:.35});
    charts.forEach(function(c){ co.observe(c.el); });
  } else { charts.forEach(function(c){ c.p = 1; c.started = true; render(c); }); }

  if (document.fonts && document.fonts.ready) document.fonts.ready.then(all);
  var rt; window.addEventListener('resize', function(){ clearTimeout(rt); rt = setTimeout(all, 120); });
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', all);
  new MutationObserver(all).observe(root, {attributes:true, attributeFilter:['data-theme']});
  document.addEventListener('visibilitychange', function(){ if (document.visibilityState === 'visible') all(); });
})();
