import json
CASOS = open("data/amd_fvg_casos.json").read()

HTML = r'''<title>AMD + FVG en el gráfico</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{
  color-scheme:light;
  --fondo:#f2f5f8; --panel:#fdfdfe; --panel2:#f6f8fb; --linea:#dde3ea;
  --tinta:#12161c; --tinta2:#4e5864; --tinta3:#8b95a1;
  --alc:#0ca30c; --baj:#d03b3b; --acc:#2a78d6; --naranja:#e08a2b;
  --gris:rgba(142,142,147,.16); --aviso-f:#fdf2f2; --aviso-b:#f0d2d2;
  --sombra:0 1px 2px rgba(16,24,40,.05), 0 1px 3px rgba(16,24,40,.04);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;
  --fondo:#10131a; --panel:#181c24; --panel2:#1d222b; --linea:#29303a;
  --tinta:#f0f3f7; --tinta2:#aab4c0; --tinta3:#6b7683;
  --alc:#22b422; --baj:#e05555; --acc:#3987e5; --naranja:#d95926;
  --gris:rgba(142,142,147,.2); --aviso-f:#2a1a1a; --aviso-b:#4a2c2c;
  --sombra:0 1px 2px rgba(0,0,0,.3);
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --fondo:#10131a; --panel:#181c24; --panel2:#1d222b; --linea:#29303a;
  --tinta:#f0f3f7; --tinta2:#aab4c0; --tinta3:#6b7683;
  --alc:#22b422; --baj:#e05555; --acc:#3987e5; --naranja:#d95926;
  --gris:rgba(142,142,147,.2); --aviso-f:#2a1a1a; --aviso-b:#4a2c2c;
  --sombra:0 1px 2px rgba(0,0,0,.3);
}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--tinta);font-size:15px;line-height:1.55;
  font-family:"IBM Plex Sans",system-ui,sans-serif}
.env{max-width:1080px;margin:0 auto;padding:22px 16px 56px}
h1{font-family:Archivo,sans-serif;font-size:26px;font-weight:700;letter-spacing:-.025em;margin:0 0 6px}
.sub{color:var(--tinta2);font-size:14.5px;margin:0 0 18px;max-width:66ch}
.pasos{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1px;
  background:var(--linea);border:1px solid var(--linea);border-radius:10px;overflow:hidden;margin-bottom:16px}
.pasos>div{background:var(--panel);padding:11px 13px}
.pasos .n{font-family:"IBM Plex Mono",monospace;font-size:11.5px;font-weight:700;letter-spacing:.06em}
.pasos b{display:block;font-size:13.5px;margin:2px 0}
.pasos p{margin:0;font-size:12.5px;color:var(--tinta2);line-height:1.45}
.caja{background:var(--panel);border:1px solid var(--linea);border-radius:11px;
  box-shadow:var(--sombra);overflow:hidden;margin-bottom:14px}
.mandos{display:flex;gap:9px;align-items:center;flex-wrap:wrap;padding:12px 15px;
  border-bottom:1px solid var(--linea);background:var(--panel2)}
button{font:inherit;font-size:14px;font-weight:600;padding:8px 14px;border:1px solid var(--linea);
  border-radius:8px;background:var(--panel);color:var(--tinta);cursor:pointer}
button:hover{background:var(--linea)} button:disabled{opacity:.35;cursor:default}
button[aria-pressed="true"]{background:var(--acc);border-color:var(--acc);color:#fff}
.cuenta{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--tinta2)}
.lienzo{overflow-x:auto;-webkit-overflow-scrolling:touch}
svg{display:block;width:100%;min-width:760px;height:auto}
.pie{display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));gap:1px;
  background:var(--linea);border-top:1px solid var(--linea)}
.pie>div{background:var(--panel);padding:10px 13px}
.pie .k{font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--tinta3);font-weight:600}
.pie .v{font-family:"IBM Plex Mono",monospace;font-size:15.5px;font-weight:600;
  font-variant-numeric:tabular-nums;margin-top:1px}
.pos{color:var(--alc)} .neg{color:var(--baj)}
.ley{display:flex;flex-wrap:wrap;gap:13px;padding:11px 15px;font-size:12.5px;color:var(--tinta2);
  border-top:1px solid var(--linea);background:var(--panel2)}
.ley span{display:flex;align-items:center;gap:6px}
.ley i{width:15px;height:11px;border-radius:2px;display:block}
.nota{font-size:13px;color:var(--tinta3);line-height:1.6;margin-top:16px}
  .aviso{background:var(--aviso-f);border:1px solid var(--aviso-b);
         border-left:3px solid var(--baj);border-radius:8px;padding:14px 16px;
         margin:18px 0 0;font-size:14px;line-height:1.55;color:var(--tinta)}
  .aviso b{color:var(--baj)}
  .aviso code{font-size:12.5px;background:var(--fondo2);padding:1px 5px;border-radius:4px}
</style>

<div class="env">
  <h1>AMD + FVG en el gráfico</h1>
  <p class="sub">Veinticuatro operaciones reales de EURUSD en H1, de las 367 que da
     la regla. Doce ganadoras y doce perdedoras, elegidas al azar.</p>

  <div class="aviso">
    <b>Corregido el 19/09/2026.</b> La primera versión de esta página decía 587
    operaciones y 76,5 % de acierto. Estaba mal: 220 de aquellas «operaciones»
    tenían el objetivo <b>ya rebasado</b> por el precio en el momento de entrar,
    así que se ganaban solas y nadie las habría puesto nunca. Quitadas ésas
    quedan 367 operaciones y <b>63,8 %</b> de acierto, que es exactamente lo que
    predice la geometría del stop y el objetivo. La regla no bate al azar.
    Explicación entera en <code>docs/CORRECCION_objetivo_rebasado.md</code>.
  </div>

  <div class="pasos">
    <div><div class="n" style="color:var(--tinta3)">A</div><b>Se aprieta</b>
      <p>8 velas de H1 en poco espacio. La caja gris.</p></div>
    <div><div class="n" style="color:var(--naranja)">M</div><b>La finta</b>
      <p>Sale de la caja y cierra de vuelta dentro.</p></div>
    <div><div class="n" style="color:var(--acc)">F</div><b>El hueco</b>
      <p>En 5 velas deja un FVG hacia el otro lado.</p></div>
    <div><div class="n" style="color:var(--acc)">→</div><b>Entras</b>
      <p>Al cierre de esa vela. Stop en la finta, objetivo al otro borde.</p></div>
  </div>

  <div class="caja">
    <div class="mandos">
      <button type="button" id="ant">← Anterior</button>
      <button type="button" id="sig">Siguiente →</button>
      <button type="button" id="fg" aria-pressed="false">Sólo ganadoras</button>
      <button type="button" id="fp" aria-pressed="false">Sólo perdedoras</button>
      <span class="cuenta" id="cnt"></span>
    </div>
    <div class="lienzo"><svg id="g" viewBox="0 0 1040 470"
         preserveAspectRatio="xMidYMid meet" role="img"
         aria-label="Una operación de AMD + FVG"></svg></div>
    <div class="pie" id="pie"></div>
    <div class="ley">
      <span><i style="background:var(--gris)"></i> la caja: el rango apretado</span>
      <span><i style="background:var(--naranja)"></i> la finta y hasta dónde llegó = tu stop</span>
      <span><i style="background:var(--acc)"></i> el hueco y la entrada</span>
      <span><i style="background:var(--alc)"></i> objetivo: el otro borde de la caja</span>
    </div>
  </div>

  <p class="nota">Velas de una hora. La caja se dibuja cuando queda confirmada, no
     antes. Todo lo que ves aquí estaba disponible en el momento de entrar: no hay
     ni una vela de futuro en la decisión.</p>
</div>

<script>
(function(){
"use strict";
var EJ = __EJ__;
var $ = function(s){ return document.querySelector(s); };
var pr = function(v){ return v.toFixed(5).replace(".", ","); };
var es = function(v,d){ return v.toLocaleString("es-ES",{minimumFractionDigits:d,maximumFractionDigits:d}); };
var filtro = 0, idx = 0;
var W=1040, H=470, ML=10, MR=104, MT=18, MB=30;

function lista(){
  return EJ.filter(function(e){ return filtro===0 || (filtro===1 ? e.gana : !e.gana); });
}
function el(t,a,x){ var s="<"+t,k; for(k in a) s+=" "+k+'="'+a[k]+'"';
  return x!==undefined ? s+">"+x+"</"+t+">" : s+"/>"; }

function pinta(){
  var L = lista(); if (!L.length) return;
  idx = Math.max(0, Math.min(L.length-1, idx));
  var E = L[idx], vs = E.velas, n = vs.length, i;
  var lo=Infinity, hi=-Infinity;
  for (i=0;i<n;i++){ if(vs[i][1]>hi) hi=vs[i][1]; if(vs[i][2]<lo) lo=vs[i][2]; }
  [E.rHi,E.rLo,E.ent,E.stop,E.obj].forEach(function(v){ if(v>hi)hi=v; if(v<lo)lo=v; });
  var pad=(hi-lo)*0.07; hi+=pad; lo-=pad;
  var pw=(W-ML-MR)/n;
  var X=function(k){ return ML+(k+0.5)*pw; };
  var Y=function(v){ return MT+(hi-v)/(hi-lo)*(H-MT-MB); };
  var an=Math.max(2.5, pw*0.62), s="";

  // la caja del rango, hasta la finta
  s += el("rect",{x:X(E.a0)-an/2-2, y:Y(E.rHi), width:X(E.m)-X(E.a0)+an+4,
      height:Math.max(1,Y(E.rLo)-Y(E.rHi)), fill:"var(--gris)",
      stroke:"var(--tinta3)","stroke-opacity":".45","stroke-dasharray":"3 3"});
  s += el("text",{x:X(E.a0), y:Y(E.rHi)-5, fill:"var(--tinta3)","font-size":11,
      "font-family":"IBM Plex Mono, monospace","font-weight":"700"},"A");

  // el hueco (FVG): entre la vela f y la f-2
  var gA = E.lado>0 ? vs[E.f][2] : vs[E.f][1];
  var gB = E.lado>0 ? vs[E.f-2][1] : vs[E.f-2][2];
  s += el("rect",{x:X(E.f-2)-an/2, y:Y(Math.max(gA,gB)),
      width:(W-MR)-(X(E.f-2)-an/2), height:Math.max(1.5,Math.abs(Y(gA)-Y(gB))),
      fill:"var(--acc)","fill-opacity":".16"});

  // bandas de riesgo y objetivo desde la entrada
  var x0=X(E.f), x1=X(E.fin);
  s += el("rect",{x:x0, y:Math.min(Y(E.ent),Y(E.stop)), width:Math.max(2,x1-x0),
      height:Math.abs(Y(E.stop)-Y(E.ent)), fill:"var(--baj)","fill-opacity":".10"});
  s += el("rect",{x:x0, y:Math.min(Y(E.ent),Y(E.obj)), width:Math.max(2,x1-x0),
      height:Math.abs(Y(E.obj)-Y(E.ent)), fill:"var(--alc)","fill-opacity":".10"});

  // horas
  for (i=0;i<n;i+=Math.ceil(n/8)){
    s += el("text",{x:X(i), y:H-MB+17, fill:"var(--tinta3)","font-size":10.5,
        "text-anchor":"middle","font-family":"IBM Plex Mono, monospace"}, E.horas[i]);
  }
  // velas
  for (i=0;i<n;i++){
    var o=vs[i][0], h=vs[i][1], l=vs[i][2], c=vs[i][3];
    var col = c>=o ? "var(--alc)" : "var(--baj)";
    var fuerte = (i===E.m || i===E.f);
    s += el("line",{x1:X(i),y1:Y(h),x2:X(i),y2:Y(l),stroke:col,
        "stroke-width":Math.max(.9,pw*.13), opacity:fuerte?1:.62});
    var y0=Y(Math.max(o,c)), y1=Y(Math.min(o,c));
    s += el("rect",{x:X(i)-an/2,y:y0,width:an,height:Math.max(1.2,y1-y0),
        fill:c>=o?"none":col, stroke:col,"stroke-width":1.2, opacity:fuerte?1:.62});
  }
  s += el("text",{x:X(E.m), y:E.lado<0 ? Y(vs[E.m][1])-6 : Y(vs[E.m][2])+14,
      fill:"var(--naranja)","font-size":12,"text-anchor":"middle","font-weight":"700",
      "font-family":"IBM Plex Mono, monospace"},"M");
  s += el("text",{x:X(E.f), y:MT+11, fill:"var(--acc)","font-size":11.5,
      "text-anchor":"middle","font-weight":"700",
      "font-family":"IBM Plex Mono, monospace"},"hueco · entras");

  // niveles con las etiquetas separadas
  var etq=[];
  [[E.stop,"var(--baj)","stop"],[E.ent,"var(--acc)","entrada"],
   [E.obj,"var(--alc)","objetivo"]].forEach(function(p){
    s += el("line",{x1:ML,y1:Y(p[0]),x2:W-MR,y2:Y(p[0]),stroke:p[1],
        "stroke-width":p[2]==="entrada"?2:1.3,
        "stroke-dasharray":p[2]==="entrada"?"":"5 4"});
    etq.push({y:Y(p[0]),col:p[1],txt:pr(p[0]),sub:p[2]});
  });
  var GAP=24; etq.sort(function(a,b){return a.y-b.y;});
  etq.forEach(function(e){ e.ye=e.y; });
  for (i=1;i<etq.length;i++) if (etq[i].ye-etq[i-1].ye<GAP) etq[i].ye=etq[i-1].ye+GAP;
  var sob = etq.length ? etq[etq.length-1].ye-(H-6) : 0;
  if (sob>0) etq.forEach(function(e){ e.ye-=sob; });
  etq.forEach(function(e){
    if (Math.abs(e.ye-e.y)>2)
      s += el("line",{x1:W-MR,y1:e.y,x2:W-MR+5,y2:e.ye,stroke:e.col,"stroke-width":1,opacity:.5});
    s += el("text",{x:W-MR+7,y:e.ye+4,fill:e.col,"font-size":11,
        "font-family":"IBM Plex Mono, monospace"}, e.txt);
    s += el("text",{x:W-MR+7,y:e.ye+14,fill:e.col,"font-size":9.5,"fill-opacity":".75",
        "font-family":"IBM Plex Sans, sans-serif"}, e.sub);
  });
  $("#g").innerHTML = s;

  var t=function(k,v,cl){ return '<div><div class="k">'+k+'</div><div class="v '+(cl||"")+'">'+v+'</div></div>'; };
  var rn = E.gana ? E.rr - E.coste/100 : -1 - E.coste/100;
  $("#pie").innerHTML =
    t("Fecha", E.fecha.slice(0,10)) + t("Hora", E.fecha.slice(11)) +
    t("Lado", E.lado>0 ? "compra" : "venta") +
    t("Riesgo", es(E.rgo,1)+" p") +
    t("R:R", es(E.rr,2)) +
    t("El coste", es(E.coste,1)+" %") +
    t("Resultado", E.gana ? "GANA" : "PIERDE", E.gana?"pos":"neg") +
    t("En R, con coste", (rn>=0?"+":"")+es(rn,2), rn>=0?"pos":"neg");
  $("#cnt").textContent = (idx+1)+" de "+L.length;
  $("#ant").disabled = idx===0;
  $("#sig").disabled = idx===L.length-1;
}
$("#ant").onclick=function(){ idx--; pinta(); };
$("#sig").onclick=function(){ idx++; pinta(); };
function marca(){ $("#fg").setAttribute("aria-pressed",String(filtro===1));
  $("#fp").setAttribute("aria-pressed",String(filtro===2)); }
$("#fg").onclick=function(){ filtro=filtro===1?0:1; idx=0; marca(); pinta(); };
$("#fp").onclick=function(){ filtro=filtro===2?0:2; idx=0; marca(); pinta(); };
marca(); pinta();
})();
</script>'''
open("docs/amd_fvg_ejemplos.html","w").write(HTML.replace("__EJ__", CASOS))
print("escrito", len(HTML.replace("__EJ__", CASOS))/1024, "KB")
