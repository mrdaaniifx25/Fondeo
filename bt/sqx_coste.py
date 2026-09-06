"""¿Sobrevive Strategy 4.3.23 al coste REAL de una cuenta de fondeo?

La especificacion asume spread 0,2 $ en el oro. En una prop firm de CFDs el
spread del XAUUSD suele ser mas ancho, y la estrategia opera de 01:30 a 23:30,
o sea tambien fuera de las horas buenas.

  python3 bt/sqx_coste.py
"""
import numpy as np, pandas as pd
exec(open("bt/sqx_controles.py").read().split("H, IDX = prepara(M)")[0])
H, IDX = prepara(M)

print(f"  {'spread':>8} {'comision':>9} {'swap':>7} | {'n':>5} {'ret':>9} "
      f"{'CAGR':>8} {'PF':>6} {'DD':>7} {'t':>6}")
base = None
for spr, com, swp in [(0.20,6,35), (0.30,6,35), (0.35,6,35), (0.50,6,35),
                      (0.65,6,35), (0.80,6,35), (1.00,6,35),
                      (0.35,10,50), (0.50,12,60), (0.20,0,0)]:
    SPREAD, COM_LOTE, SWAP = spr, com, swp
    g = dict(globals()); g.update(SPREAD=spr, COM_LOTE=com, SWAP=swp)
    exec(compile(open("bt/sqx_controles.py").read().split("H, IDX = prepara(M)")[0]
         .split("M = pd.concat")[0], "<c>", "exec"), g)
    R = g["corre"](M, H, IDX, filtro=False) if False else None
    # llamada directa con los costes cambiados
    import types
    fn = corre.__globals__
    fn["SPREAD"], fn["COM_LOTE"], fn["SWAP"] = spr, com, swp
    R = corre(M, H, IDX, filtro=False)
    if base is None: base = R
    an = 3.55
    print(f"  {spr:8.2f} {com:9.0f} {swp:7.0f} | {R['n']:>5} {R['ret']*100:>8.1f}% "
          f"{((1+R['ret'])**(1/an)-1)*100:>7.2f}% {R['pf']:>6.3f} "
          f"{R['dd']*100:>6.1f}% {R['t']:>+6.2f}", flush=True)
print("\n  (sin filtro GannHiLo, que el control 2 demostro que no aporta)")
print("  la ultima fila es SIN NINGUN COSTE: el techo teorico")
