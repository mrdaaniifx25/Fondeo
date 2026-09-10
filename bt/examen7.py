"""Construye paginas/examen7.html a partir del motor del bloque 5.

Cambia: los datos, la clave de guardado, el sorteo del indicador, y sustituye
la tabla del bloque 5 por LA CAPA DEL INDICADOR -flechas sobre las velas y el
panel de pine/londres_roturas.pine-.

  python3 bt/examen7.py
"""
import json, re

html = open("paginas/examen5.html", encoding="utf-8").read()
SES  = open("data/examen_sesiones7.json", encoding="utf-8").read()
IND  = json.load(open("data/examen7_ind.json"))
con  = sorted(int(k) for k, v in IND["con"].items() if v)

def rep(viejo, nuevo, n=1):
    global html
    assert viejo in html, viejo[:70]
    html = html.replace(viejo, nuevo, n)

# ─── 1 · datos, clave de guardado y sorteo ────────────────────────────────
html = re.sub(r"const SES = \[.*?\];\n", "const SES = " + SES + ";\n", html,
              count=1, flags=re.S)
rep('CLAVE = "examen-londres-5a"', 'CLAVE = "examen-londres-7a"')
html = re.sub(r"const CON_IND = new Set\(\[[^\]]*\]\);",
              "const CON_IND = new Set(" + json.dumps(con) + ");\n"
              "const CAND = " + json.dumps(IND["cand"], separators=(",", ":")) + ";",
              html, count=1)
rep('<span style="color:var(--tenue)"> / 50</span>',
    '<span style="color:var(--tenue)"> / 40</span>')
rep("<title>El examen de Londres · bloque 5</title>",
    "<title>El examen de Londres · bloque 7</title>") if \
    "<title>El examen de Londres · bloque 5</title>" in html else None

# ─── 2 · dibuja() acepta marcas del indicador ─────────────────────────────
rep("""  const {w, h, niveles = [], pos = null, escala = null, cuantas = 70,
         posEscala = false} = opts;""",
    """  const {w, h, niveles = [], pos = null, escala = null, cuantas = 70,
         posEscala = false, marcas = []} = opts;""")

rep("""  s += `<text x="${MI+1}" y="${h-3}" fill="var(--tenue)" font-family="IBM Plex Mono,monospace" font-size="9.5">${hhmm(d[0][0])}</text>`""",
    """  if (marcas.length){
    const pos1 = new Map(d.map((v,k) => [v[0], MI + k*paso + paso/2]));
    for (const mk of marcas){
      const x = pos1.get(mk.m); if (x === undefined) continue;
      const v = d[d.findIndex(z => z[0] === mk.m)];
      const arr = mk.lado > 0, col = arr ? "var(--alza)" : "var(--baja)";
      if (!mk.pasa){
        const yy = arr ? y(P(v[3])) + 9 : y(P(v[2])) - 9;
        s += `<path d="M ${x} ${yy + (arr?-4:4)} l -3.4 ${arr?5:-5} l 6.8 0 z" fill="var(--tenue)" opacity=".85"/>`;
        continue;
      }
      const yy = arr ? y(P(v[3])) + 20 : y(P(v[2])) - 20;
      s += `<path d="M ${x} ${yy + (arr?-7:7)} l -4.6 ${arr?7:-7} l 9.2 0 z" fill="${col}"/>`
         + `<rect x="${x-24}" y="${yy-(arr?6:11)}" width="48" height="14" rx="2" fill="${col}"/>`
         + `<text x="${x}" y="${yy+(arr?4.5:-0.5)}" text-anchor="middle" fill="var(--ficha)" `
         + `font-family="IBM Plex Sans Condensed,sans-serif" font-size="9.5" font-weight="700" `
         + `letter-spacing=".06em">${arr ? "COMPRA" : "VENTA"}</text>`;
    }
  }
  s += `<text x="${MI+1}" y="${h-3}" fill="var(--tenue)" font-family="IBM Plex Mono,monospace" font-size="9.5">${hhmm(d[0][0])}</text>`""")

# ─── 3 · el panel, con lo que dice el indicador de verdad ─────────────────
viejo = html[html.index("function indicador(p, c){"):html.index("\n}", html.index("function indicador(p, c){"))+2]
nuevo = '''function cands(){ return (CAND[String(ses().n)] || []).filter(x => x.m <= S.t); }
function refM5(){
  const g = Math.floor(S.t/5) - 1, v = serie("m5", 5);
  for (let k = v.length-1; k >= 0; k--) if (Math.floor(v[k][0]/5) === g) return v[k];
  return null;
}
function indicador(p, c){
  const cs = cands(), fl = cs.filter(x => x.pasa);
  const viva = cs.length && cs[cs.length-1].m >= S.t - 2 ? cs[cs.length-1] : null;
  const u = refM5();
  const pct = u ? Math.round(Math.abs(P(u[4])-P(u[1]))/Math.max(P(u[2])-P(u[3]), 1e-9)*100) : null;
  const lleno = pct !== null && pct >= 80;
  const nd = fl.length, sobra = nd >= 3;
  const lot = viva && viva.pips > 0 ? (CUENTA*RIESGO)/(viva.pips*10) : null;
  const fila = (a, b, cc, col) => `<tr><td${col?` style="color:${col}"`:""}>${a}</td>`
    + `<td${col?` style="color:${col}"`:""}>${b}</td>`
    + `<td${col?` style="color:${col}"`:""}>${cc}</td></tr>`;
  return `<table>
    ${fila("candidatas hoy", nd, sobra ? "YA VAS SOBRADO" : "una o dos, no más",
           sobra ? "var(--baja)" : "var(--tinta)")}
    ${fila("cuerpo de la M5 de referencia", pct === null ? "—" : pct + " %",
           lleno ? "LLENO · descartada" : "normal",
           lleno ? "var(--baja)" : "var(--alza)")}
    ${viva
      ? fila("candidata viva", (viva.lado > 0 ? "COMPRA" : "VENTA") + " en " + P(viva.ent).toFixed(5),
             viva.pips.toFixed(1).replace(".", ",") + " p · " + (lot ? lot.toFixed(2) : "—") + " lotes",
             viva.pasa ? (viva.lado > 0 ? "var(--alza)" : "var(--baja)") : "var(--tenue)")
      : fila("candidata viva", "—", "esperando rotura", "var(--tenue)")}
    <tr class="ver"><td colspan="3" style="color:var(--tenue)">la flecha sola acierta
      el 31-38 % · lo que vale +16 puntos es cuál eliges tú</td></tr>
  </table>`;
}
'''
html = html.replace(viejo, nuevo, 1)

# ─── 4 · las marcas y el cuerpo de la M5 en el gráfico de M1 ──────────────
rep("""  escM1 = dibuja($("gm1"), m1Vis(), {w:W, h:H, niveles:niv, pos:cajaViva(), posEscala:true,
                                     escala: arrastrando ? escFija : null, cuantas:90});""",
    """  const nivM1 = niv.slice();
  if (conInd()){
    const u = refM5();
    if (u){ const a = Math.min(P(u[1]), P(u[4])), b = Math.max(P(u[1]), P(u[4]));
            nivM1.push([a, "var(--marca)", ""], [b, "var(--marca)", "CUERPO M5"]); }
  }
  escM1 = dibuja($("gm1"), m1Vis(), {w:W, h:H, niveles:nivM1, pos:cajaViva(), posEscala:true,
                                     escala: arrastrando ? escFija : null, cuantas:90,
                                     marcas: conInd() ? cands() : []});""")

open("paginas/examen7.html", "w", encoding="utf-8").write(html)
print(f"paginas/examen7.html · {len(html)/1024:,.0f} KB")
print(f"  {len(json.loads(SES))} sesiones · indicador en {len(con)}: {con}")
