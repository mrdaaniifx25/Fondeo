import json, io
CASOS = open("data/etiquetas_casos_3tf.json").read()

HTML = r'''<title>300 setups a ciegas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{
  --fondo:#F4F6F9; --panel:#FFFFFF; --hueco:#EAEEF4; --linea:#D8DEE8;
  --texto:#171B22; --suave:#69717F; --tenue:#98A0AE;
  --alc:#2E9E85; --baj:#C0563A; --acc:#3D6FB4; --acc-sua:#E4EDF9;
  --avi:#B07D1F;
  --sombra:0 1px 2px rgba(20,26,38,.06), 0 8px 24px rgba(20,26,38,.06);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --fondo:#0F1319; --panel:#181D26; --hueco:#131820; --linea:#2A313D;
    --texto:#E3E8F0; --suave:#8D96A6; --tenue:#5E6879;
    --alc:#3FB89C; --baj:#D86E50; --acc:#6D9DDF; --acc-sua:#1C2836;
    --avi:#D9A93F;
    --sombra:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
  }
}
:root[data-theme="dark"]{
  --fondo:#0F1319; --panel:#181D26; --hueco:#131820; --linea:#2A313D;
  --texto:#E3E8F0; --suave:#8D96A6; --tenue:#5E6879;
  --alc:#3FB89C; --baj:#D86E50; --acc:#6D9DDF; --acc-sua:#1C2836;
  --avi:#D9A93F;
  --sombra:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--fondo); color:var(--texto);
  font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:15px; line-height:1.5; -webkit-font-smoothing:antialiased;
}
.envoltura{max-width:1240px; margin:0 auto; padding:18px 20px 28px; display:flex; flex-direction:column; gap:14px; min-height:100vh}

/* ── cabecera ───────────────────────────────────────── */
.cab{display:flex; align-items:baseline; gap:14px; flex-wrap:wrap}
.cab h1{margin:0; font-size:19px; font-weight:600; letter-spacing:-.01em}
.cab .sub{color:var(--suave); font-size:13.5px}
.cab .der{margin-left:auto; display:flex; gap:8px; align-items:center}

.barra{height:5px; background:var(--hueco); border-radius:3px; overflow:hidden; display:flex}
.barra i{display:block; height:100%}
.barra .b{background:var(--acc)} .barra .m{background:var(--tenue)} .barra .s{background:var(--linea)}

.cuenta{display:flex; gap:16px; font-size:12.5px; color:var(--suave);
  font-family:"IBM Plex Mono",ui-monospace,monospace; font-variant-numeric:tabular-nums}
.cuenta b{color:var(--texto); font-weight:600}

/* ── tarjeta principal ──────────────────────────────── */
.tarjeta{background:var(--panel); border:1px solid var(--linea); border-radius:12px;
  box-shadow:var(--sombra); display:grid; grid-template-columns:1fr 232px; overflow:hidden}
@media (max-width:820px){ .tarjeta{grid-template-columns:1fr} }

.lienzo{padding:9px 6px 9px 11px; min-width:0; display:grid;
  grid-template-columns:1fr 1fr; align-content:start; gap:7px 12px}
@media (max-width:820px){ .lienzo{grid-template-columns:1fr} }
.panel{min-width:0; display:flex; flex-direction:column; gap:2px}
.panel.ancho{grid-column:1 / -1}
@media (max-width:820px){ .panel.ancho{grid-column:auto} }
.panel .tf{font-size:10.5px; text-transform:uppercase; letter-spacing:.085em;
  color:var(--tenue); font-weight:600; padding-left:3px}
.panel .tf b{color:var(--suave); font-weight:600}
svg.g{width:100%; height:auto; display:block}

.datos{border-left:1px solid var(--linea); padding:16px 16px 14px; display:flex; flex-direction:column; gap:14px; background:var(--hueco)}
@media (max-width:820px){ .datos{border-left:none; border-top:1px solid var(--linea)} }

.marca{font-size:11px; text-transform:uppercase; letter-spacing:.09em; color:var(--tenue); font-weight:600}
.sentido{font-size:20px; font-weight:700; letter-spacing:-.01em; margin-top:2px}
.sentido.c{color:var(--alc)} .sentido.v{color:var(--baj)}

dl.lista{margin:0; display:grid; grid-template-columns:auto 1fr; gap:7px 12px; font-size:13px}
dl.lista dt{color:var(--suave)}
dl.lista dd{margin:0; text-align:right; font-family:"IBM Plex Mono",ui-monospace,monospace;
  font-variant-numeric:tabular-nums; font-weight:500}
dd.res{color:var(--avi)}

.nota{font-size:12px; color:var(--tenue); line-height:1.45; border-top:1px solid var(--linea); padding-top:11px; margin-top:auto}

/* ── botonera ───────────────────────────────────────── */
.juicio{display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px}
button{font:inherit; cursor:pointer; border-radius:9px; border:1px solid var(--linea);
  background:var(--panel); color:var(--texto); padding:13px 10px; transition:.13s ease;
  display:flex; flex-direction:column; align-items:center; gap:3px}
button:hover{border-color:var(--acc); transform:translateY(-1px)}
button:focus-visible{outline:2px solid var(--acc); outline-offset:2px}
button .t{font-weight:600; font-size:14.5px}
button .k{font-size:11px; color:var(--tenue); font-family:"IBM Plex Mono",monospace}
button.bu{border-color:var(--acc); background:var(--acc-sua)}
button.bu .t{color:var(--acc)}
button.sel{box-shadow:inset 0 0 0 2px var(--acc)}

.pie{display:flex; gap:10px; align-items:center; flex-wrap:wrap; font-size:12.5px; color:var(--suave)}
.pie button{padding:7px 13px; flex-direction:row; font-size:13px}
.pie .esp{margin-left:auto}
.pie .nube{color:var(--tenue);font-size:12.5px}
.pie .nube.avisa{color:var(--avi)}

kbd{font-family:"IBM Plex Mono",monospace; font-size:11.5px; background:var(--hueco);
  border:1px solid var(--linea); border-bottom-width:2px; border-radius:4px; padding:1px 5px; color:var(--suave)}

/* ── despliegues ────────────────────────────────────── */
details{background:var(--panel); border:1px solid var(--linea); border-radius:10px; padding:0}
details summary{cursor:pointer; padding:11px 15px; font-size:13.5px; font-weight:500; list-style:none}
details summary::-webkit-details-marker{display:none}
details summary::before{content:"▸ "; color:var(--tenue)}
details[open] summary::before{content:"▾ "}
details .cuerpo{padding:0 15px 15px; font-size:13.5px; color:var(--suave); line-height:1.6}
details .cuerpo strong{color:var(--texto); font-weight:600}
details .cuerpo ul{margin:8px 0 0; padding-left:19px} details .cuerpo li{margin:4px 0}
textarea{width:100%; height:110px; font-family:"IBM Plex Mono",monospace; font-size:11.5px;
  background:var(--hueco); color:var(--texto); border:1px solid var(--linea); border-radius:7px; padding:9px; resize:vertical}
.fin{text-align:center; padding:44px 20px; color:var(--suave)}
.fin h2{color:var(--texto); font-size:22px; margin:0 0 8px}
@media (prefers-reduced-motion:reduce){ *{transition:none !important; animation:none !important} }
</style>

<div class="envoltura">
  <div class="cab">
    <h1>300 setups a ciegas</h1>
    <span class="sub">marca los que <em>tú</em> operarías</span>
    <span class="der cuenta" id="cuenta"></span>
  </div>
  <div class="barra" id="barra"></div>

  <div class="tarjeta" id="tarjeta">
    <div class="lienzo">
      <div class="panel"><span class="tf">H4 · <b>el rango y el barrido</b></span>
        <svg class="g" id="g4" viewBox="0 0 520 304" preserveAspectRatio="xMidYMid meet"></svg></div>
      <div class="panel"><span class="tf">H1 · <b>el mismo rango de cerca</b></span>
        <svg class="g" id="g1" viewBox="0 0 520 304" preserveAspectRatio="xMidYMid meet"></svg></div>
      <div class="panel ancho"><span class="tf">M5 · <b>la entrada</b></span>
        <svg class="g" id="g5" viewBox="0 0 1064 262" preserveAspectRatio="xMidYMid meet"></svg></div>
    </div>
    <div class="datos" id="datos"></div>
  </div>

  <div class="juicio">
    <button id="bB" class="bu"><span class="t">Lo operaría</span><span class="k">1 · B</span></button>
    <button id="bM"><span class="t">No lo operaría</span><span class="k">2 · M</span></button>
    <button id="bS"><span class="t">No lo veo claro</span><span class="k">3 · S</span></button>
  </div>

  <div class="pie">
    <button id="atras">← Atrás</button>
    <span>Teclado: <kbd>1</kbd><kbd>2</kbd><kbd>3</kbd> para marcar, <kbd>←</kbd> para volver</span>
    <span class="nube" id="nube">conectando…</span>
    <span class="esp" id="guardado"></span>
  </div>

  <details>
    <summary>Qué estás mirando, y qué decide cada marca</summary>
    <div class="cuerpo">
      <p>Cada caso es un <strong>CRT ya formado</strong>: una vela base de H4 define un rango, la
      siguiente se lleva uno de sus extremos con la mecha y cierra dentro. Ese barrido está
      marcado en el gráfico. La entrada es el cierre de esa vela, el stop va al extremo del
      barrido y el objetivo al extremo opuesto de la vela base.</p>
      <ul>
        <li><strong>Lo operaría</strong> — con lo que ves, tú entrarías aquí.</li>
        <li><strong>No lo operaría</strong> — el setup existe pero no te gusta.</li>
        <li><strong>No lo veo claro</strong> — no te decides. Se queda fuera del análisis.</li>
      </ul>
      <p>El gráfico se corta en la vela de entrada: <strong>no hay ni una vela posterior</strong>,
      así que no puedes ver cómo acabó. Yo tampoco te muestro el resultado. El orden va barajado
      y la muestra es aleatoria, no elegida.</p>
      <p>Marca con tu criterio, no intentes adivinar qué quiero oír. Si marcas todo que sí, o todo
      que no, el análisis no puede decir nada.</p>
    </div>
  </details>

  <details id="expo">
    <summary>Guardar y enviarme los resultados</summary>
    <div class="cuerpo">
      <p>Se guarda <strong>en la nube</strong> según vas marcando, así que puedes cerrar
      esto y seguir otro día, o desde otro aparato. Yo puedo leerlo directamente: no hace falta
      que me pegues nada. Esta caja es solo la red de seguridad por si la nube fallara.</p>
      <textarea id="salida" readonly></textarea>
      <div style="display:flex;gap:8px;margin-top:9px;align-items:center">
        <button id="copiar">Copiar</button>
        <button id="borrar">Empezar de cero</button>
        <span id="avisoCopia" style="font-size:12.5px"></span>
      </div>
    </div>
  </details>
</div>

<script>
const CASOS = __DATOS__;
const CLAVE = "crt_etiquetas_v1";
let marcas = {}, i = 0;

try { const g = localStorage.getItem(CLAVE); if (g) marcas = JSON.parse(g) || {}; } catch(e) {}
i = CASOS.findIndex(c => !marcas[c.id]); if (i < 0) i = CASOS.length;

function guarda(){
  try { localStorage.setItem(CLAVE, JSON.stringify(marcas)); } catch(e) {}
  const n = Object.keys(marcas).length;
  document.getElementById("guardado").textContent = n ? n + " guardadas en este navegador" : "";
  document.getElementById("salida").value = exporta();
}
function exporta(){
  const p = CASOS.filter(c => marcas[c.id]).map(c => c.id + ":" + marcas[c.id]);
  return "ETIQUETAS v1 · " + p.length + " de " + CASOS.length + "\n" + p.join(" ");
}
function cuentas(){
  let b=0,m=0,s=0;
  for (const k in marcas){ const v = marcas[k]; if(v==="b")b++; else if(v==="m")m++; else s++; }
  return {b,m,s,t:b+m+s};
}
function pintaProgreso(){
  const c = cuentas(), N = CASOS.length;
  document.getElementById("cuenta").innerHTML =
    "<span><b>"+c.t+"</b>/"+N+"</span><span>sí <b>"+c.b+"</b></span>"+
    "<span>no <b>"+c.m+"</b></span><span>duda <b>"+c.s+"</b></span>";
  const bar = document.getElementById("barra");
  bar.innerHTML = "";
  [["b",c.b],["m",c.m],["s",c.s]].forEach(([k,v]) => {
    const e = document.createElement("i");
    e.className = k; e.style.width = (100*v/N) + "%"; bar.appendChild(e);
  });
}

function fmt(v, d){ return v.toFixed(d); }

const NS = "http://www.w3.org/2000/svg";
function el(t, a, txt){
  let s = "<" + t;
  for (const k in a) s += " " + k + '="' + a[k] + '"';
  return txt !== undefined ? s + ">" + txt + "</" + t + ">" : s + "/>";
}

/* Un panel. `vs` son las velas, `off` el desplazamiento del primer precio
   dentro de cada fila (H4 lleva la marca de tiempo delante, H1 y M5 no).
   Todos los paneles terminan en la vela de entrada: no hay ni una posterior. */
function panel(id, vs, off, c, cfg){
  const svg = document.getElementById(id);
  const vb = svg.getAttribute("viewBox").split(" ");
  const W = +vb[2], H = +vb[3], mI = 8, mD = 66, mA = 13, mB = 16;
  let lo = Infinity, hi = -Infinity;
  vs.forEach(v => { hi = Math.max(hi, v[off+1]); lo = Math.min(lo, v[off+2]); });
  [c.stop, c.objetivo, c.entrada, c.rango_hi, c.rango_lo].forEach(v => {
    hi = Math.max(hi, v); lo = Math.min(lo, v); });
  if (cfg.dia) [c.dia_hi, c.dia_lo].forEach(v => { hi = Math.max(hi,v); lo = Math.min(lo,v); });
  const pad = (hi - lo) * 0.08; hi += pad; lo -= pad;
  const Y = p => mA + (hi - p) / (hi - lo) * (H - mA - mB);
  const paso = (W - mI - mD) / vs.length;
  const X = k => mI + paso * (k + 0.5);
  const anch = Math.max(2, paso * 0.6);
  let out = "";

  // el rango de la vela base, marcado igual en los tres marcos
  const xr = cfg.iBase >= 0 ? X(cfg.iBase) - anch/2 - 2 : mI;
  out += el("rect", {x:xr, y:Y(c.rango_hi), width:(W-mD)-xr,
      height:Math.max(1, Y(c.rango_lo)-Y(c.rango_hi)), fill:"var(--acc)", "fill-opacity":".07"});
  out += el("rect", {x:xr, y:Y(c.rango_hi), width:(W-mD)-xr,
      height:Math.max(1, Y(c.rango_lo)-Y(c.rango_hi)), fill:"none", stroke:"var(--acc)",
      "stroke-opacity":".35", "stroke-dasharray":"3 4"});
  out += el("text", {x:mI+3, y:Y(c.rango_hi)-5, fill:"var(--acc)", "font-size":10,
      "font-family":"IBM Plex Mono, monospace", "fill-opacity":".85"}, "rango");

  // etiquetas del eje derecho: se recogen y se apartan al final, porque
  // entrada, stop y objetivo se pisan cuando el stop es estrecho
  const etq = [];
  if (cfg.dia) [[c.dia_hi,"PDH"],[c.dia_lo,"PDL"]].forEach(([p,et]) => {
    out += el("line", {x1:mI, y1:Y(p), x2:W-mD, y2:Y(p), stroke:"var(--tenue)",
        "stroke-width":1, "stroke-dasharray":"2 5"});
    etq.push({y:Y(p), col:"var(--tenue)", txt:et, sub:""});
  });

  vs.forEach((v, k) => {
    const o = v[off], h = v[off+1], l = v[off+2], cl = v[off+3];
    const sube = cl >= o, col = sube ? "var(--alc)" : "var(--baj)";
    const esBase = k === cfg.iBase, esEnt = k >= cfg.iEnt;
    const op = (esBase || esEnt) ? 1 : .5;
    out += el("line", {x1:X(k), y1:Y(h), x2:X(k), y2:Y(l), stroke:col, "stroke-width":1.2, opacity:op});
    const y0 = Y(Math.max(o,cl)), y1 = Y(Math.min(o,cl));
    out += el("rect", {x:X(k)-anch/2, y:y0, width:anch, height:Math.max(1.3, y1-y0),
        fill:sube?"none":col, stroke:col, "stroke-width":1.2, opacity:op});
  });

  // el tramo que barre el rango, encuadrado
  if (cfg.iEnt >= 0 && cfg.iEnt < vs.length){
    let eh = -Infinity, elo = Infinity;
    for (let k = cfg.iEnt; k < vs.length; k++){
      eh = Math.max(eh, vs[k][off+1]); elo = Math.min(elo, vs[k][off+2]); }
    const x0 = X(cfg.iEnt) - anch/2 - 3;
    out += el("rect", {x:x0, y:Y(eh)-3, width:(W-mD)-x0-1, height:Y(elo)-Y(eh)+6,
        fill:"none", stroke:"var(--texto)", "stroke-width":1.1, "stroke-opacity":".4", rx:3});
    out += el("text", {x:Math.min(x0+3, W-mD-42), y:Y(elo)+13, fill:"var(--texto)",
        "font-size":10, "font-family":"IBM Plex Mono, monospace", "fill-opacity":".6"}, "barrido");
  }
  if (cfg.iBase >= 0){
    out += el("text", {x:Math.min(X(cfg.iBase), W-mD-18), y:Y(c.rango_lo)+13,
        fill:"var(--acc)", "font-size":10, "text-anchor":"middle",
        "font-family":"IBM Plex Mono, monospace"}, "base");
  }

  [[c.entrada,"var(--acc)","entrada",1.8,""],
   [c.stop,"var(--baj)","stop",1.3,"5 4"],
   [c.objetivo,"var(--alc)","objetivo",1.3,"5 4"]].forEach(([p,col,et,w,dash]) => {
    const a = {x1:mI, y1:Y(p), x2:W-mD, y2:Y(p), stroke:col, "stroke-width":w};
    if (dash) a["stroke-dasharray"] = dash;
    out += el("line", a);
    etq.push({y:Y(p), col:col, txt:fmt(p, c.dec), sub:et});
  });

  const HUE = 23;
  etq.sort((a,b) => a.y - b.y);
  etq.forEach(e => { e.ye = e.y; });
  for (let k = 1; k < etq.length; k++)
    if (etq[k].ye - etq[k-1].ye < HUE) etq[k].ye = etq[k-1].ye + HUE;
  const sobra = etq.length ? etq[etq.length-1].ye - (H - 4) : 0;
  if (sobra > 0) etq.forEach(e => { e.ye -= sobra; });
  etq.forEach(e => {
    if (Math.abs(e.ye - e.y) > 2)
      out += el("line", {x1:W-mD, y1:e.y, x2:W-mD+4, y2:e.ye, stroke:e.col,
          "stroke-width":1, opacity:.5});
    out += el("text", {x:W-mD+6, y:e.ye+3.5, fill:e.col, "font-size":10,
        "font-family":"IBM Plex Mono, monospace"}, e.txt);
    if (e.sub) out += el("text", {x:W-mD+6, y:e.ye+13, fill:e.col, "font-size":9,
        "fill-opacity":".7", "font-family":"IBM Plex Sans, sans-serif"}, e.sub);
  });
  svg.innerHTML = out;
}

/* En el movil no caben 60 velas de M5 legibles. Se recorta POR LA IZQUIERDA,
   nunca por la derecha: la ultima vela sigue siendo la de entrada. */
function recorta(vs, iBase, iEnt, max){
  if (vs.length <= max) return [vs, iBase, iEnt];
  const s = vs.length - max;
  return [vs.slice(s), iBase - s >= 0 ? iBase - s : -1, Math.max(0, iEnt - s)];
}

function dibuja(c){
  const movil = window.innerWidth < 820;
  const caja = movil ? "0 0 384 300" : null;
  if (movil){
    ["g4","g1","g5"].forEach(k => document.getElementById(k).setAttribute("viewBox", caja));
  } else {
    document.getElementById("g4").setAttribute("viewBox", "0 0 520 304");
    document.getElementById("g1").setAttribute("viewBox", "0 0 520 304");
    document.getElementById("g5").setAttribute("viewBox", "0 0 1064 262");
  }
  const [w4, b4, e4] = recorta(c.velas, c.i_base, c.i_ent, movil ? 18 : 99);
  const [w1, b1, e1] = recorta(c.v1,    c.i_base1, c.i_ent1, movil ? 26 : 99);
  const [w5, b5, e5] = recorta(c.v5,    -1,        c.i_ent5, movil ? 36 : 99);
  panel("g4", w4, 1, c, {iBase:b4, iEnt:e4, dia:true});
  panel("g1", w1, 0, c, {iBase:b1, iEnt:e1, dia:false});
  panel("g5", w5, 0, c, {iBase:b5, iEnt:e5, dia:false});
}

let anchoPrev = window.innerWidth < 820, temporizador = 0;
window.addEventListener("resize", () => {
  const ahora = window.innerWidth < 820;
  if (ahora === anchoPrev) return;
  anchoPrev = ahora;
  clearTimeout(temporizador);
  temporizador = setTimeout(() => { if (i < CASOS.length) dibuja(CASOS[i]); }, 120);
});

function pinta(){
  if (i >= CASOS.length){ acaba(); return; }
  const c = CASOS[i];
  dibuja(c);
  const dir = c.largo ? "COMPRA" : "VENTA";
  const bias = c.dia_crt === 0 ? "sin señal"
             : (c.dia_crt > 0 ? "compra" : "venta");
  document.getElementById("datos").innerHTML =
    '<div><div class="marca">Caso ' + c.n + ' de ' + CASOS.length + '</div>' +
    '<div class="sentido ' + (c.largo?"c":"v") + '">' + dir + '</div></div>' +
    '<dl class="lista">' +
    '<dt>Activo</dt><dd>' + c.ins + '</dd>' +
    '<dt>Marco</dt><dd>H4</dd>' +
    '<dt>Cierre vela</dt><dd>' + c.hora + '</dd>' +
    '<dt>Entrada</dt><dd>' + fmt(c.entrada,c.dec) + '</dd>' +
    '<dt>Stop</dt><dd>' + fmt(c.stop,c.dec) + '</dd>' +
    '<dt>Objetivo</dt><dd>' + fmt(c.objetivo,c.dec) + '</dd>' +
    '<dt>Riesgo</dt><dd>' + c.riesgo + (c.ins==="NAS100"?" pts":" pips") + '</dd>' +
    '<dt>R:R</dt><dd>' + c.rr.toFixed(2) + '</dd>' +
    '<dt>Coste</dt><dd class="res">' + c.coste_pct + ' % del riesgo</dd>' +
    '<dt>CRT diario</dt><dd>' + bias + '</dd>' +
    '</dl>' +
    '<div class="nota">Los tres marcos terminan en el mismo instante: el cierre de la vela del barrido. No hay nada después.</div>';
  ["bB","bM","bS"].forEach(id => document.getElementById(id).classList.remove("sel"));
  const y = marcas[c.id];
  if (y) document.getElementById(y==="b"?"bB":y==="m"?"bM":"bS").classList.add("sel");
  document.getElementById("atras").disabled = i === 0;
  pintaProgreso();
}

function acaba(){
  const c = cuentas();
  document.getElementById("tarjeta").innerHTML =
    '<div class="fin" style="grid-column:1/-1"><h2>Terminado</h2>' +
    '<p>' + c.b + ' que operarías, ' + c.m + ' que no, ' + c.s + ' en duda.</p>' +
    '<p>Abre <strong>Guardar y enviarme los resultados</strong> aquí abajo, copia el texto y pégamelo en el chat.</p></div>';
  document.querySelector(".juicio").style.display = "none";
  document.getElementById("expo").open = true;
  pintaProgreso(); guarda();
}

function marca(v){
  if (i >= CASOS.length) return;
  marcas[CASOS[i].id] = v;
  hayCambio = true;
  guarda(); i++; pinta();
}
document.getElementById("bB").onclick = () => marca("b");
document.getElementById("bM").onclick = () => marca("m");
document.getElementById("bS").onclick = () => marca("s");
document.getElementById("atras").onclick = () => { if (i > 0){ i--; pinta(); } };
document.addEventListener("keydown", e => {
  if (e.target.tagName === "TEXTAREA") return;
  if (e.key === "1" || e.key.toLowerCase() === "b") marca("b");
  else if (e.key === "2" || e.key.toLowerCase() === "m") marca("m");
  else if (e.key === "3" || e.key.toLowerCase() === "s") marca("s");
  else if (e.key === "ArrowLeft" && i > 0){ i--; pinta(); }
  else return;
  e.preventDefault();
});
document.getElementById("copiar").onclick = async () => {
  const t = document.getElementById("salida");
  const a = document.getElementById("avisoCopia");
  try { await navigator.clipboard.writeText(t.value); a.textContent = "Copiado"; }
  catch(e){ t.select(); a.textContent = "Selecciónalo y copia con Ctrl+C"; }
  setTimeout(() => a.textContent = "", 2600);
};
document.getElementById("borrar").onclick = async () => {
  if (!confirm("Se borran todas tus marcas. ¿Seguro?")) return;
  marcas = {}; i = 0;
  try { localStorage.removeItem(CLAVE); } catch(e) {}
  if (DB) { try { await DB.doc("etiquetas/v1").delete(); } catch(e) {} }
  location.reload();
};
guarda(); pinta();

/* Guardado en la nube. El navegador es la copia inmediata; la nube es la que
   sobrevive a cerrar la pestaña, y la que yo puedo leer sin que pegues nada.
   Nada se escribe hasta haber leído lo que ya había: si no, una pestaña recién
   abierta borraría el trabajo de la anterior. */
let DB = null, listoNube = false, hayCambio = false, escribiendo = false;

function estadoNube(t, avisa){
  const e = document.getElementById("nube");
  if (!e) return;
  e.textContent = t;
  e.className = "nube" + (avisa ? " avisa" : "");
}

async function vuelcaNube(){
  if (!DB || !listoNube || escribiendo || !hayCambio) return;
  escribiendo = true; hayCambio = false;
  const n = Object.keys(marcas).length;
  try {
    await DB.doc("etiquetas/v1").set({
      marcas: marcas, n: n, version: 1, actualizado: new Date().toISOString() });
    estadoNube(n + " guardadas en la nube");
  } catch (err) {
    hayCambio = true;
    estadoNube("la nube falló — copia el texto de abajo", true);
  }
  escribiendo = false;
}
setInterval(vuelcaNube, 2500);

(async function(){
  try { DB = await claude.use("db"); } catch (e) { DB = null; }
  if (!DB){
    estadoNube("sin nube: solo en este navegador, copia el texto de abajo", true);
    return;
  }
  try {
    const s = await DB.doc("etiquetas/v1").get();
    const guardadas = (s.exists && s.data() ? s.data().marcas : null) || {};
    if (Object.keys(guardadas).length > Object.keys(marcas).length){
      marcas = guardadas;
      i = CASOS.findIndex(c => !marcas[c.id]);
      if (i < 0) i = CASOS.length;
      guarda(); pinta();
    }
  } catch (e) {
    estadoNube("no he podido leer la nube — no marques aún, recarga", true);
    return;
  }
  listoNube = true;
  estadoNube(Object.keys(marcas).length + " guardadas en la nube");
})();
</script>'''

open("docs/etiquetado_criterio.html","w").write(
    HTML.replace("__DATOS__", CASOS))
print("escrito", len(HTML.replace("__DATOS__", CASOS))/1024, "KB")
