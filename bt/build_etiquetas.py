import json, io
CASOS = open("data/etiquetas_casos.json").read()

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
.envoltura{max-width:1180px; margin:0 auto; padding:18px 20px 28px; display:flex; flex-direction:column; gap:14px; min-height:100vh}

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
  box-shadow:var(--sombra); display:grid; grid-template-columns:1fr 232px; overflow:hidden; flex:1}
@media (max-width:820px){ .tarjeta{grid-template-columns:1fr} }

.lienzo{padding:6px 4px 0 10px; min-width:0; display:flex; flex-direction:column}
svg.g{width:100%; height:100%; min-height:330px; display:block}

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
    <div class="lienzo"><svg class="g" id="g" preserveAspectRatio="none"></svg></div>
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
      <p>Se guarda solo en este navegador según vas marcando. <strong>Copia esto y pégamelo en el
      chat</strong> cada 50 o así, por si acaso.</p>
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

function dibuja(c){
  const svg = document.getElementById("g");
  const W = 1000, H = 460, mI = 8, mD = 74, mA = 16, mB = 26;
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  const vs = c.velas;
  let lo = Infinity, hi = -Infinity;
  vs.forEach(v => { hi = Math.max(hi, v[2]); lo = Math.min(lo, v[3]); });
  [c.stop, c.objetivo, c.entrada, c.dia_hi, c.dia_lo].forEach(v => { hi = Math.max(hi,v); lo = Math.min(lo,v); });
  const pad = (hi - lo) * 0.07; hi += pad; lo -= pad;
  const Y = p => mA + (hi - p) / (hi - lo) * (H - mA - mB);
  const paso = (W - mI - mD) / vs.length;
  const X = k => mI + paso * (k + 0.5);
  const anch = Math.max(3, paso * 0.6);

  const NS = "http://www.w3.org/2000/svg";
  let out = "";
  const el = (t, a, txt) => {
    let s = "<" + t;
    for (const k in a) s += " " + k + '="' + a[k] + '"';
    return txt !== undefined ? s + ">" + txt + "</" + t + ">" : s + "/>";
  };

  // banda del rango de la vela base
  const vb = vs[c.i_base];
  out += el("rect", {x:X(c.i_base)-anch/2-2, y:Y(vb[2]), width:(W-mD)-(X(c.i_base)-anch/2-2),
      height:Math.max(1,Y(vb[3])-Y(vb[2])), fill:"var(--acc)", "fill-opacity":".07"});
  out += el("rect", {x:X(c.i_base)-anch/2-2, y:Y(vb[2]), width:(W-mD)-(X(c.i_base)-anch/2-2),
      height:Math.max(1,Y(vb[3])-Y(vb[2])), fill:"none", stroke:"var(--acc)",
      "stroke-opacity":".35", "stroke-dasharray":"3 4"});

  // niveles del día anterior
  [[c.dia_hi,"PDH"],[c.dia_lo,"PDL"]].forEach(([p,et]) => {
    out += el("line", {x1:mI, y1:Y(p), x2:W-mD, y2:Y(p), stroke:"var(--tenue)",
        "stroke-width":1, "stroke-dasharray":"2 5"});
    out += el("text", {x:W-mD+5, y:Y(p)+3.5, fill:"var(--tenue)", "font-size":11,
        "font-family":"IBM Plex Mono, monospace"}, et);
  });

  // velas
  vs.forEach((v, k) => {
    const [t,o,h,l,cl] = v;
    const sube = cl >= o;
    const col = sube ? "var(--alc)" : "var(--baj)";
    const esBase = k === c.i_base, esEnt = k === c.i_ent;
    const op = (esBase || esEnt) ? 1 : .55;
    out += el("line", {x1:X(k), y1:Y(h), x2:X(k), y2:Y(l), stroke:col, "stroke-width":1.4, opacity:op});
    const y0 = Y(Math.max(o,cl)), y1 = Y(Math.min(o,cl));
    out += el("rect", {x:X(k)-anch/2, y:y0, width:anch, height:Math.max(1.5, y1-y0),
        fill:sube?"none":col, stroke:col, "stroke-width":1.4, opacity:op});
    if (esEnt){
      out += el("rect", {x:X(k)-anch/2-4, y:Y(h)-4, width:anch+8, height:Y(l)-Y(h)+8,
          fill:"none", stroke:"var(--texto)", "stroke-width":1.2, "stroke-opacity":".45", rx:3});
      out += el("text", {x:X(k), y:Y(l)+16, fill:"var(--texto)", "font-size":10.5,
          "text-anchor":"middle", "font-family":"IBM Plex Mono, monospace", "fill-opacity":".65"}, "barrido");
    }
    if (esBase){
      out += el("text", {x:X(k), y:Y(vb[2])-6, fill:"var(--acc)", "font-size":10.5,
          "text-anchor":"middle", "font-family":"IBM Plex Mono, monospace"}, "base");
    }
  });

  // entrada, stop, objetivo
  const niv = [[c.entrada,"var(--acc)","entrada",2,""],
               [c.stop,"var(--baj)","stop",1.4,"5 4"],
               [c.objetivo,"var(--alc)","objetivo",1.4,"5 4"]];
  niv.forEach(([p,col,et,w,dash]) => {
    const a = {x1:X(c.i_ent)-anch, y1:Y(p), x2:W-mD, y2:Y(p), stroke:col, "stroke-width":w};
    if (dash) a["stroke-dasharray"] = dash;
    out += el("line", a);
    out += el("text", {x:W-mD+5, y:Y(p)+3.5, fill:col, "font-size":11,
        "font-family":"IBM Plex Mono, monospace"}, fmt(p, c.dec));
    out += el("text", {x:W-mD+5, y:Y(p)+15, fill:col, "font-size":9.5, "fill-opacity":".7",
        "font-family":"IBM Plex Sans, sans-serif"}, et);
  });
  svg.innerHTML = out;
}

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
    '<div class="nota">El gráfico termina en la vela del barrido. No hay nada después.</div>';
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
document.getElementById("borrar").onclick = () => {
  if (!confirm("Se borran todas tus marcas. ¿Seguro?")) return;
  marcas = {}; i = 0;
  try { localStorage.removeItem(CLAVE); } catch(e) {}
  location.reload();
};
guarda(); pinta();
</script>'''

open("/tmp/claude-0/-home-user-Fondeo/0d8c92b4-16e7-53a1-886b-22385a3d6383/scratchpad/etiquetas.html","w").write(
    HTML.replace("__DATOS__", CASOS))
print("escrito", len(HTML.replace("__DATOS__", CASOS))/1024, "KB")
