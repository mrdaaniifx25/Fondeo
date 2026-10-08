import json
CASOS = open("data/barridos_casos.json").read()
SAL   = open("data/barridos_salidas.json").read()
MAR   = json.dumps(json.load(open("/tmp/claude-0/-home-user-Fondeo/0d8c92b4-16e7-53a1-886b-22385a3d6383/scratchpad/barridos/v1.json")).get("data", {}).get("marcas", {}), separators=(",",":"))

HTML = r'''<title>Dónde estaba la buena</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{
  color-scheme:light;
  --fondo:#F4F6F9; --panel:#fff; --hueco:#EAEEF4; --linea:#D8DEE8;
  --texto:#171B22; --suave:#69717F; --tenue:#98A0AE;
  --alc:#2E9E85; --baj:#C0563A; --acc:#3D6FB4; --acc-sua:#E4EDF9;
  --ok:#17914F; --mal:#C23B36;
  --sombra:0 1px 2px rgba(20,26,38,.06), 0 8px 24px rgba(20,26,38,.06);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;
  --fondo:#0F1319; --panel:#181D26; --hueco:#131820; --linea:#2A313D;
  --texto:#E3E8F0; --suave:#8D96A6; --tenue:#5E6879;
  --alc:#3FB89C; --baj:#D86E50; --acc:#6D9DDF; --acc-sua:#1C2836;
  --ok:#2FB86A; --mal:#E0554F;
  --sombra:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --fondo:#0F1319; --panel:#181D26; --hueco:#131820; --linea:#2A313D;
  --texto:#E3E8F0; --suave:#8D96A6; --tenue:#5E6879;
  --alc:#3FB89C; --baj:#D86E50; --acc:#6D9DDF; --acc-sua:#1C2836;
  --ok:#2FB86A; --mal:#E0554F;
  --sombra:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--texto);
  font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:15px;line-height:1.55}
.env{max-width:1100px;margin:0 auto;padding:18px 16px 40px;display:flex;
  flex-direction:column;gap:13px}
h1{margin:0;font-size:22px;font-weight:700;letter-spacing:-.02em}
.sub{color:var(--suave);font-size:14px;margin:0;max-width:64ch}
.leyenda{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;color:var(--suave)}
.leyenda span{display:flex;align-items:center;gap:6px}
.pas{width:13px;height:13px;border-radius:3px;display:block}

.tarj{background:var(--panel);border:1px solid var(--linea);border-radius:12px;
  box-shadow:var(--sombra);overflow:hidden}
.info{display:flex;gap:15px;flex-wrap:wrap;padding:11px 15px;
  border-bottom:1px solid var(--linea);background:var(--hueco);font-size:13px}
.info span{font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}
.info b{font-family:"IBM Plex Sans",sans-serif;color:var(--suave);font-weight:500}
.sent{font-weight:700} .sent.c{color:var(--alc)} .sent.v{color:var(--baj)}
.lienzo{padding:6px 2px 0 8px}
svg{width:100%;height:auto;display:block}
.mandos{display:flex;gap:9px;align-items:center;flex-wrap:wrap;padding:12px 15px;
  border-top:1px solid var(--linea)}
button{font:inherit;font-size:14px;font-weight:600;padding:9px 15px;cursor:pointer;
  border:1px solid var(--linea);border-radius:9px;background:var(--panel);color:var(--texto)}
button:hover{border-color:var(--acc)} button:disabled{opacity:.35;cursor:default}
.cnt{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--suave)}

.res{background:var(--panel);border:1px solid var(--linea);border-radius:12px;
  box-shadow:var(--sombra);padding:16px 18px}
.res h2{font-size:18px;margin:0 0 10px;font-weight:700;letter-spacing:-.01em}
.envt{overflow-x:auto}
table{width:100%;min-width:430px;border-collapse:collapse;font-size:13.5px;
  font-variant-numeric:tabular-nums}
th{text-align:right;font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--tenue);font-weight:600;padding:7px 9px;border-bottom:1px solid var(--linea)}
th:first-child{text-align:left}
td{text-align:right;padding:7px 9px;border-bottom:1px solid var(--hueco);
  font-family:"IBM Plex Mono",monospace}
td:first-child{text-align:left;font-family:inherit}
.neg{color:var(--mal)}
.rem{border-left:3px solid var(--mal);background:var(--hueco);border-radius:0 9px 9px 0;
  padding:12px 15px;margin-top:14px;font-size:14px}
.rem b{color:var(--mal)}
.disp{display:flex;align-items:flex-end;gap:4px;height:74px;margin:10px 0 4px}
.disp i{flex:1;background:var(--acc);border-radius:3px 3px 0 0;display:block;min-height:2px}
.disp-et{display:flex;gap:4px;font-size:10px;color:var(--tenue);
  font-family:"IBM Plex Mono",monospace}
.disp-et span{flex:1;text-align:center}
</style>

<div class="env">
  <h1>Dónde estaba la buena</h1>
  <p class="sub">Los mismos 60 barridos que marcaste. En cada uno he probado
     <strong>entrar en todas y cada una de las velas</strong> y he mirado cómo acabó.</p>

  <div class="leyenda">
    <span><i class="pas" style="background:var(--ok)"></i> entrar aquí llegaba al objetivo</span>
    <span><i class="pas" style="background:var(--mal)"></i> entrar aquí se comía el stop</span>
    <span><i class="pas" style="background:var(--acc)"></i> donde entraste tú</span>
  </div>

  <div class="tarj">
    <div class="info" id="info"></div>
    <div class="lienzo"><svg id="g" viewBox="0 0 1040 430"
         preserveAspectRatio="xMidYMid meet" role="img"
         aria-label="Un barrido con el resultado de cada entrada posible"></svg></div>
    <div class="mandos">
      <button id="ant">← Anterior</button>
      <button id="sig">Siguiente →</button>
      <span class="cnt" id="cnt"></span>
    </div>
  </div>

  <div class="res">
    <h2>Y ahora júntalos todos</h2>
    <p class="sub">Entrando siempre en la misma vela, en los 60 casos:</p>
    <div class="envt">
    <table>
      <thead><tr><th>entras en</th><th>acierto</th><th>riesgo</th>
        <th>coste %R</th><th>neta</th></tr></thead>
      <tbody id="tabla"></tbody>
    </table>
    </div>

    <p class="sub" style="margin-top:16px">Y aquí está dónde cae <strong>la mejor
       vela</strong> de cada caso:</p>
    <div class="disp" id="disp"></div>
    <div class="disp-et" id="disp-et"></div>

    <div class="rem">
      <b>No hay una buena.</b> Las trece posiciones pierden, todas. Y la mejor de
      cada caso cae en un sitio distinto cada vez, repartida por toda la ventana
      sin ningún patrón. En un barrido típico <b>ganan 2 de las 13 velas</b>, y
      cuáles son sólo se sabe después.
    </div>
  </div>
</div>

<script>
(function(){
"use strict";
var CASOS = __CASOS__, SAL = __SAL__, MAR = __MAR__;
var i = 0;
var $ = function(s){ return document.querySelector(s); };
function el(t, a, txt){
  var s = "<" + t, k;
  for (k in a) s += " " + k + '="' + a[k] + '"';
  return txt !== undefined ? s + ">" + txt + "</" + t + ">" : s + "/>";
}
function pr(v){ return v.toFixed(5).replace(".", ","); }

function dibuja(c){
  var W = 1040, H = 430, mI = 8, mD = 98, mA = 16, mB = 42;
  var vs = c.velas, n = vs.length, k;
  var lo = Infinity, hi = -Infinity;
  for (k = 0; k < n; k++){ if (vs[k][1] > hi) hi = vs[k][1]; if (vs[k][2] < lo) lo = vs[k][2]; }
  [c.niv, c.ext].forEach(function(v){ if (v > hi) hi = v; if (v < lo) lo = v; });
  var pad = (hi - lo) * 0.08; hi += pad; lo -= pad;
  var Y = function(p){ return mA + (hi - p) / (hi - lo) * (H - mA - mB); };
  var paso = (W - mI - mD) / n;
  var X = function(j){ return mI + paso * (j + 0.5); };
  var an = Math.max(3, paso * 0.62);
  var out = "", S = SAL[c.id] || [], mio = MAR[c.id];

  [[c.niv, "var(--acc)", "nivel", "4 4"], [c.ext, "var(--texto)", "stop", ""]].forEach(function(p){
    out += el("line", {x1:mI, y1:Y(p[0]), x2:W-mD, y2:Y(p[0]), stroke:p[1],
        "stroke-width":1.5, "stroke-dasharray":p[3]});
    out += el("text", {x:W-mD+6, y:Y(p[0])+4, fill:p[1], "font-size":11,
        "font-family":"IBM Plex Mono, monospace"}, p[2] + " " + pr(p[0]));
  });

  for (k = 0; k < n; k++){
    var o = vs[k][0], h = vs[k][1], l = vs[k][2], cl = vs[k][3];
    var sube = cl >= o, col = sube ? "var(--alc)" : "var(--baj)";
    out += el("line", {x1:X(k), y1:Y(h), x2:X(k), y2:Y(l), stroke:col, "stroke-width":1.3});
    var y0 = Y(Math.max(o, cl)), y1 = Y(Math.min(o, cl));
    out += el("rect", {x:X(k)-an/2, y:y0, width:an, height:Math.max(1.5, y1-y0),
        fill:sube ? "none" : col, stroke:col, "stroke-width":1.3});
    if (k === c.i_barr)
      out += el("rect", {x:X(k)-an/2-3, y:Y(h)-3, width:an+6, height:Y(l)-Y(h)+6,
          fill:"none", stroke:"var(--texto)", "stroke-width":1.4, rx:3});
  }

  // la tira de resultados, una casilla por vela candidata
  var yT = H - mB + 8;
  S.forEach(function(r){
    if (!r) return;
    var c2 = r.gana ? "var(--ok)" : "var(--mal)";
    out += el("rect", {x:X(r.j)-an/2, y:yT, width:an, height:11, rx:2.5, fill:c2});
    if (r.gana)
      out += el("text", {x:X(r.j), y:yT-3, fill:"var(--ok)", "font-size":11,
          "text-anchor":"middle", "font-weight":"700"}, "✓");
  });
  if (typeof mio === "number"){
    out += el("rect", {x:X(mio)-an/2-3.5, y:yT-3.5, width:an+7, height:18, rx:4,
        fill:"none", stroke:"var(--acc)", "stroke-width":2.2});
    out += el("text", {x:X(mio), y:H-6, fill:"var(--acc)", "font-size":10.5,
        "text-anchor":"middle", "font-weight":"600",
        "font-family":"IBM Plex Mono, monospace"}, "tú");
  }
  $("#g").innerHTML = out;
}

function pinta(){
  var c = CASOS[i], S = SAL[c.id] || [];
  var g = S.filter(function(r){ return r && r.gana; }).length;
  var t = S.filter(function(r){ return r; }).length;
  dibuja(c);
  var mio = MAR[c.id];
  var suyo = (typeof mio === "number")
      ? (S.find(function(r){ return r && r.j === mio; }) || {}) : null;
  $("#info").innerHTML =
    '<span class="sent ' + (c.lado > 0 ? "c" : "v") + '">' +
      (c.lado > 0 ? "COMPRA" : "VENTA") + '</span>' +
    '<span><b>fecha</b> ' + c.hora + '</span>' +
    '<span><b>sesión</b> ' + c.ses + '</span>' +
    '<span><b>ganan</b> ' + g + ' de ' + t + ' velas</span>' +
    (suyo && suyo.j !== undefined
      ? '<span><b>la tuya</b> ' + (suyo.gana ? "ganó" : "perdió") + '</span>'
      : '<span><b>la tuya</b> la descartaste</span>');
  $("#cnt").textContent = (i + 1) + " de " + CASOS.length;
  $("#ant").disabled = i === 0;
  $("#sig").disabled = i === CASOS.length - 1;
}
$("#ant").onclick = function(){ i--; pinta(); };
$("#sig").onclick = function(){ i++; pinta(); };

// tabla por desfase y reparto de la mejor vela
(function(){
  var filas = [], mejor = [], off, k;
  for (off = 0; off < 13; off++){
    var rs = [];
    CASOS.forEach(function(c){
      var S = SAL[c.id] || [];
      if (S[off]) rs.push(S[off]);
    });
    if (rs.length < 15) continue;
    var gan = rs.filter(function(r){ return r.gana; }).length;
    var rg = rs.map(function(r){ return r.rgo; }).sort(function(a,b){ return a-b; });
    var med = rg[Math.floor(rg.length/2)];
    var nt = rs.reduce(function(s,r){ return s + r.Rn; }, 0) / rs.length;
    filas.push('<tr><td>+' + off + (off === 0 ? " (la del barrido)" : " velas") + '</td>' +
      '<td>' + (100*gan/rs.length).toFixed(1).replace(".",",") + ' %</td>' +
      '<td>' + med.toFixed(1).replace(".",",") + ' p</td>' +
      '<td>' + (100*1.43/med).toFixed(0) + ' %</td>' +
      '<td class="neg">' + nt.toFixed(3).replace(".",",") + '</td></tr>');
  }
  $("#tabla").innerHTML = filas.join("");

  var cuenta = new Array(13).fill(0);
  CASOS.forEach(function(c){
    var S = (SAL[c.id] || []).filter(function(r){ return r; });
    if (!S.length) return;
    var b = S.reduce(function(a, r){ return r.Rn > a.Rn ? r : a; }, S[0]);
    var o = b.j - c.i_barr;
    if (o >= 0 && o < 13) cuenta[o]++;
  });
  var mx = Math.max.apply(null, cuenta);
  $("#disp").innerHTML = cuenta.map(function(v){
    return '<i style="height:' + Math.max(2, 100*v/mx) + '%"></i>'; }).join("");
  $("#disp-et").innerHTML = cuenta.map(function(v, k){
    return "<span>+" + k + "</span>"; }).join("");
})();

pinta();
})();
</script>'''

out = HTML.replace("__CASOS__", CASOS).replace("__SAL__", SAL).replace("__MAR__", MAR)
open("docs/barridos_buena.html", "w").write(out)
print("escrito", len(out)/1024, "KB")
