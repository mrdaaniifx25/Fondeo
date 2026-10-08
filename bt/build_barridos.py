import json
CASOS = open("data/barridos_casos.json").read()

HTML = r'''<title>Dónde entras</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{
  color-scheme:light;
  --fondo:#F4F6F9; --panel:#fff; --hueco:#EAEEF4; --linea:#D8DEE8;
  --texto:#171B22; --suave:#69717F; --tenue:#98A0AE;
  --alc:#2E9E85; --baj:#C0563A; --acc:#3D6FB4; --acc-sua:#E4EDF9; --avi:#B07D1F;
  --sombra:0 1px 2px rgba(20,26,38,.06), 0 8px 24px rgba(20,26,38,.06);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;
  --fondo:#0F1319; --panel:#181D26; --hueco:#131820; --linea:#2A313D;
  --texto:#E3E8F0; --suave:#8D96A6; --tenue:#5E6879;
  --alc:#3FB89C; --baj:#D86E50; --acc:#6D9DDF; --acc-sua:#1C2836; --avi:#D9A93F;
  --sombra:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --fondo:#0F1319; --panel:#181D26; --hueco:#131820; --linea:#2A313D;
  --texto:#E3E8F0; --suave:#8D96A6; --tenue:#5E6879;
  --alc:#3FB89C; --baj:#D86E50; --acc:#6D9DDF; --acc-sua:#1C2836; --avi:#D9A93F;
  --sombra:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--texto);
  font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:15px;line-height:1.5}
.env{max-width:1100px;margin:0 auto;padding:16px 16px 34px;display:flex;
  flex-direction:column;gap:12px}
.cab{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.cab h1{margin:0;font-size:19px;font-weight:600;letter-spacing:-.01em}
.cab .sub{color:var(--suave);font-size:13.5px}
.cab .der{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:12.5px;
  color:var(--suave);font-variant-numeric:tabular-nums}
.cab .der b{color:var(--texto)}
.barra{height:5px;background:var(--hueco);border-radius:3px;overflow:hidden;display:flex}
.barra i{display:block;height:100%}
.barra .e{background:var(--acc)} .barra .n{background:var(--tenue)}

.aviso{background:var(--acc-sua);border:1px solid var(--linea);border-radius:10px;
  padding:11px 14px;font-size:13.5px;color:var(--suave)}
.aviso b{color:var(--texto)}

.tarj{background:var(--panel);border:1px solid var(--linea);border-radius:12px;
  box-shadow:var(--sombra);overflow:hidden}
.info{display:flex;gap:16px;flex-wrap:wrap;padding:11px 15px;
  border-bottom:1px solid var(--linea);background:var(--hueco);font-size:13px}
.info span{font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}
.info b{font-family:"IBM Plex Sans",sans-serif;color:var(--suave);font-weight:500}
.sent{font-weight:700} .sent.c{color:var(--alc)} .sent.v{color:var(--baj)}
.lienzo{padding:6px 2px 0 8px}
svg{width:100%;height:auto;display:block;touch-action:manipulation}
svg rect.pick{cursor:pointer}

.pie{display:flex;gap:9px;align-items:center;flex-wrap:wrap;padding:12px 15px;
  border-top:1px solid var(--linea)}
button{font:inherit;font-size:14px;font-weight:600;padding:10px 15px;cursor:pointer;
  border:1px solid var(--linea);border-radius:9px;background:var(--panel);color:var(--texto)}
button:hover{border-color:var(--acc)}
button:disabled{opacity:.35;cursor:default}
button.salto{background:var(--hueco)}
.est{margin-left:auto;font-size:12.5px;color:var(--tenue)}
.est.avisa{color:var(--avi)}
.nota{font-size:12.5px;color:var(--tenue);line-height:1.55}
.fin{text-align:center;padding:40px 20px;color:var(--suave)}
.fin h2{color:var(--texto);font-size:21px;margin:0 0 6px}
:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
</style>

<div class="env">
  <div class="cab">
    <h1>Dónde entras</h1>
    <span class="sub">toca la vela en la que abrirías</span>
    <span class="der" id="cuenta"></span>
  </div>
  <div class="barra" id="barra"></div>

  <div class="aviso">
    Esto <b>no es una prueba</b>, es para que yo aprenda tu entrada. Por eso se ven
    velas después del barrido: sin ellas no podrías señalar nada. Toca la vela donde
    abrirías la operación, o dale a <b>«ésta no la tomo»</b> si la descartarías.
  </div>

  <div class="tarj" id="tarj">
    <div class="info" id="info"></div>
    <div class="lienzo"><svg id="g" viewBox="0 0 1040 430"
         preserveAspectRatio="xMidYMid meet" role="img"
         aria-label="Un barrido de nivel de sesión"></svg></div>
    <div class="pie">
      <button id="atras">← Atrás</button>
      <button id="salto" class="salto">Ésta no la tomo</button>
      <span class="est" id="est">conectando…</span>
    </div>
  </div>

  <p class="nota">La línea azul es el extremo de la sesión de referencia. La línea
     negra es hasta dónde llegó el barrido, que es donde iría el stop. La vela con
     el borde marcado es la que cierra de vuelta dentro del nivel.</p>
</div>

<script>
(function(){
"use strict";
var CASOS = __DATOS__;
var CLAVE = "barridos_v1";
var marcas = {}, i = 0, DB = null, listo = false, sucio = false, escribiendo = false;
var $ = function(s){ return document.querySelector(s); };

try { var g = localStorage.getItem(CLAVE); if (g) marcas = JSON.parse(g) || {}; } catch(e){}
i = CASOS.findIndex(function(c){ return !marcas[c.id]; });
if (i < 0) i = CASOS.length;

function guarda(){
  try { localStorage.setItem(CLAVE, JSON.stringify(marcas)); } catch(e){}
  sucio = true;
}
function estado(t, avisa){
  var e = $("#est"); e.textContent = t; e.className = "est" + (avisa ? " avisa" : "");
}
function progreso(){
  var ks = Object.keys(marcas), ent = 0, no = 0, k;
  for (k in marcas){ if (marcas[k] === "no") no++; else ent++; }
  $("#cuenta").innerHTML = "<b>" + ks.length + "</b>/" + CASOS.length +
    " · entra <b>" + ent + "</b> · descarta <b>" + no + "</b>";
  var b = $("#barra"); b.innerHTML = "";
  [["e", ent], ["n", no]].forEach(function(p){
    var e = document.createElement("i");
    e.className = p[0]; e.style.width = (100 * p[1] / CASOS.length) + "%";
    b.appendChild(e);
  });
}
function el(t, a, txt){
  var s = "<" + t, k;
  for (k in a) s += " " + k + '="' + a[k] + '"';
  return txt !== undefined ? s + ">" + txt + "</" + t + ">" : s + "/>";
}
function pr(v){ return v.toFixed(5).replace(".", ","); }

function dibuja(c){
  var W = 1040, H = 430, mI = 8, mD = 98, mA = 16, mB = 30;
  var vs = c.velas, n = vs.length, k;
  var lo = Infinity, hi = -Infinity;
  for (k = 0; k < n; k++){ if (vs[k][1] > hi) hi = vs[k][1]; if (vs[k][2] < lo) lo = vs[k][2]; }
  [c.niv, c.ext].forEach(function(v){ if (v > hi) hi = v; if (v < lo) lo = v; });
  var pad = (hi - lo) * 0.08; hi += pad; lo -= pad;
  var Y = function(p){ return mA + (hi - p) / (hi - lo) * (H - mA - mB); };
  var paso = (W - mI - mD) / n;
  var X = function(j){ return mI + paso * (j + 0.5); };
  var an = Math.max(3, paso * 0.62);
  var out = "";

  // zona posterior al barrido, para que se vea donde se puede elegir
  out += el("rect", {x:X(c.i_barr) + paso/2, y:mA, width:(W-mD) - (X(c.i_barr)+paso/2),
      height:H-mA-mB, fill:"var(--acc)", "fill-opacity":".05"});

  [[c.niv, "var(--acc)", "nivel", "4 4"], [c.ext, "var(--texto)", "stop", ""]].forEach(function(p){
    out += el("line", {x1:mI, y1:Y(p[0]), x2:W-mD, y2:Y(p[0]), stroke:p[1],
        "stroke-width":1.5, "stroke-dasharray":p[3]});
    out += el("text", {x:W-mD+6, y:Y(p[0])+4, fill:p[1], "font-size":11,
        "font-family":"IBM Plex Mono, monospace"}, p[2] + " " + pr(p[0]));
  });

  for (k = 0; k < n; k++){
    var o = vs[k][0], h = vs[k][1], l = vs[k][2], cl = vs[k][3];
    var sube = cl >= o, col = sube ? "var(--alc)" : "var(--baj)";
    var marcada = marcas[c.id] === k;
    out += el("line", {x1:X(k), y1:Y(h), x2:X(k), y2:Y(l), stroke:col, "stroke-width":1.3});
    var y0 = Y(Math.max(o, cl)), y1 = Y(Math.min(o, cl));
    out += el("rect", {x:X(k)-an/2, y:y0, width:an, height:Math.max(1.5, y1-y0),
        fill:sube ? "none" : col, stroke:col, "stroke-width":1.3});
    if (k === c.i_barr){
      out += el("rect", {x:X(k)-an/2-3, y:Y(h)-3, width:an+6, height:Y(l)-Y(h)+6,
          fill:"none", stroke:"var(--texto)", "stroke-width":1.4, rx:3});
      out += el("text", {x:X(k), y:H-mB+13, fill:"var(--texto)", "font-size":10.5,
          "text-anchor":"middle", "font-family":"IBM Plex Mono, monospace"}, "barrido");
    }
    if (marcada){
      out += el("rect", {x:X(k)-an/2-4, y:mA, width:an+8, height:H-mA-mB,
          fill:"var(--acc)", "fill-opacity":".16", stroke:"var(--acc)", "stroke-width":2, rx:4});
      out += el("text", {x:X(k), y:mA-3, fill:"var(--acc)", "font-size":11,
          "text-anchor":"middle", "font-weight":"600",
          "font-family":"IBM Plex Mono, monospace"}, "ENTRAS");
    }
  }
  // zonas tocables, solo de la vela del barrido en adelante
  for (k = c.i_barr; k < n; k++){
    out += el("rect", {"class":"pick", "data-k":k, x:X(k)-paso/2, y:mA,
        width:paso, height:H-mA-mB, fill:"transparent"});
  }
  $("#g").innerHTML = out;
}

function pinta(){
  if (i >= CASOS.length){
    $("#tarj").innerHTML = '<div class="fin"><h2>Ya está</h2>' +
      '<p>Las ' + CASOS.length + ' marcadas. Dímelo y las leo.</p></div>';
    progreso(); return;
  }
  var c = CASOS[i];
  dibuja(c);
  $("#info").innerHTML =
    '<span class="sent ' + (c.lado > 0 ? "c" : "v") + '">' +
      (c.lado > 0 ? "COMPRA" : "VENTA") + '</span>' +
    '<span><b>caso</b> ' + c.n + "/" + CASOS.length + '</span>' +
    '<span><b>sesión</b> ' + c.ses + '</span>' +
    '<span><b>fecha</b> ' + c.hora + '</span>' +
    '<span><b>barrido</b> ' + c.rgo + ' p</span>';
  $("#atras").disabled = i === 0;
  progreso();
}

function marca(v){
  if (i >= CASOS.length) return;
  marcas[CASOS[i].id] = v;
  guarda(); i++; pinta();
}
$("#g").addEventListener("click", function(ev){
  var t = ev.target;
  if (!t || !t.getAttribute) return;
  var k = t.getAttribute("data-k");
  if (k === null) return;
  marca(parseInt(k, 10));
});
$("#salto").onclick = function(){ marca("no"); };
$("#atras").onclick = function(){ if (i > 0){ i--; pinta(); } };

async function vuelca(){
  if (!DB || !listo || escribiendo || !sucio) return;
  escribiendo = true; sucio = false;
  var n = Object.keys(marcas).length;
  try {
    await DB.doc("barridos/v1").set({ marcas: marcas, n: n,
      actualizado: new Date().toISOString() });
    estado(n + " guardadas en la nube");
  } catch (e){ sucio = true; estado("la nube falló, sigue en el navegador", true); }
  escribiendo = false;
}
setInterval(vuelca, 2500);

(async function(){
  try { DB = await claude.use("db"); } catch(e){ DB = null; }
  if (!DB){ estado("sin nube: solo en este navegador", true); pinta(); return; }
  try {
    var s = await DB.doc("barridos/v1").get();
    var g = (s.exists && s.data() ? s.data().marcas : null) || {};
    if (Object.keys(g).length > Object.keys(marcas).length){
      marcas = g;
      i = CASOS.findIndex(function(c){ return !marcas[c.id]; });
      if (i < 0) i = CASOS.length;
    }
  } catch(e){ estado("no he podido leer la nube, recarga", true); pinta(); return; }
  listo = true;
  estado(Object.keys(marcas).length + " guardadas en la nube");
  pinta();
})();

pinta();
})();
</script>'''

open("docs/barridos_entrada.html", "w").write(HTML.replace("__DATOS__", CASOS))
print("escrito", len(HTML.replace("__DATOS__", CASOS)) / 1024, "KB")
