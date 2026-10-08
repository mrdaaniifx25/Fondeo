"""Dibuja, en SVG puro, lo que habrias tenido puesto mes a mes en tres pares."""
import numpy as np, pandas as pd
exec(open("bt/sistema.py").read().split('print("="*112); print("EL SISTEMA")')[0])
sm, sk = sig_mom(), sig_carry()
SEN = (0.5*sm.add(sk.reindex_like(sm).fillna(0), fill_value=0)).where(OKm)
SEN = SEN.where(SEN.abs() >= 0.25, 0.0)

PARES = [("United Kingdom","GBPUSD", False), ("Japan","USDJPY", True),
         ("Euro","EURUSD", False)]
DESDE = "2019-01-01"
W, H, PAD, GAP = 980, 230, 52, 26
partes = []
for k, (pais, nom, inv) in enumerate(PARES):
    p = P[pais][P.index >= DESDE]                     # moneda por dolar
    s = SEN[pais].reindex(p.index).fillna(0)
    px = 1.0/p if not inv else p                      # como lo cotiza el broker
    y0 = k*(H+GAP)
    lo, hi = float(px.min()), float(px.max()); rg = hi-lo or 1
    n = len(px)
    fx = lambda i: PAD + (W-PAD-18)*i/max(n-1,1)
    fy = lambda v: y0+26 + (H-52)*(1-(v-lo)/rg)
    # el SIGNO es sobre la moneda extranjera; si el par es USDXXX se invierte
    lado = (-s if inv else s)
    bandas = []
    i = 0
    while i < n:
        v = np.sign(lado.iloc[i])
        if v == 0: i += 1; continue
        j = i
        while j+1 < n and np.sign(lado.iloc[j+1]) == v: j += 1
        c = "#0b6e4f" if v > 0 else "#a83318"
        bandas.append(f'<rect x="{fx(i):.1f}" y="{y0+26:.1f}" width="{max(fx(j)-fx(i),1.5):.1f}" '
                      f'height="{H-52}" fill="{c}" opacity="0.13"/>')
        i = j+1
    linea = " ".join(f"{fx(i):.1f},{fy(float(v)):.1f}" for i, v in enumerate(px))
    ejes = ""
    for yy, et in ((lo, f"{lo:.4f}"), (hi, f"{hi:.4f}")):
        ejes += (f'<text x="{PAD-8:.0f}" y="{fy(yy)+4:.1f}" font-size="10" fill="#8b96a3" '
                 f'text-anchor="end" font-family="monospace">{et}</text>')
    anios = ""
    for a in range(int(px.index[0].year)+1, int(px.index[-1].year)+1):
        idx = [i for i, d in enumerate(px.index) if d.year == a and d.month == 1]
        if idx:
            anios += (f'<line x1="{fx(idx[0]):.1f}" y1="{y0+26}" x2="{fx(idx[0]):.1f}" '
                      f'y2="{y0+H-26}" stroke="#dfe4ea" stroke-width="1"/>'
                      f'<text x="{fx(idx[0]):.1f}" y="{y0+H-10}" font-size="10" fill="#8b96a3" '
                      f'text-anchor="middle" font-family="monospace">{a}</text>')
    giros = sum(1 for i in range(1, n) if np.sign(lado.iloc[i]) != np.sign(lado.iloc[i-1]))
    partes.append(
        f'<text x="{PAD}" y="{y0+16}" font-size="13" font-weight="600" fill="#131920" '
        f'font-family="sans-serif">{nom}</text>'
        f'<text x="{W-18}" y="{y0+16}" font-size="11" fill="#8b96a3" text-anchor="end" '
        f'font-family="sans-serif">{giros} cambios en {n} meses</text>'
        + anios + "".join(bandas) + ejes +
        f'<polyline points="{linea}" fill="none" stroke="#131920" stroke-width="1.6" '
        f'stroke-linejoin="round"/>')

alto = len(PARES)*(H+GAP) + 34
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {alto}" width="{W}" '
       f'height="{alto}" font-family="sans-serif">'
       f'<rect width="{W}" height="{alto}" fill="#ffffff"/>' + "".join(partes) +
       f'<g transform="translate({PAD},{alto-12})">'
       f'<rect x="0" y="-9" width="11" height="11" fill="#0b6e4f" opacity="0.5"/>'
       f'<text x="16" y="0" font-size="11" fill="#56626f">comprado</text>'
       f'<rect x="86" y="-9" width="11" height="11" fill="#a83318" opacity="0.5"/>'
       f'<text x="102" y="0" font-size="11" fill="#56626f">vendido</text>'
       f'<text x="176" y="0" font-size="11" fill="#8b96a3">'
       f'sin color = la señal no llega a 0,25 y te quedas fuera</text></g></svg>')
open("docs/img/senal_ejemplos.svg", "w").write(svg)
print("docs/img/senal_ejemplos.svg escrito")
for pais, nom, inv in PARES:
    s = SEN[pais][SEN.index >= DESDE].fillna(0)
    lado = (-s if inv else s)
    print(f"  {nom}: {sum(1 for i in range(1,len(lado)) if np.sign(lado.iloc[i])!=np.sign(lado.iloc[i-1]))} "
          f"cambios · {100*(lado!=0).mean():.0f} % del tiempo con posicion")
