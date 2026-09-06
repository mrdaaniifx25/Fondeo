"""¿Que aporta un activo casi perfectamente anticorrelacionado? Cero, y se ve.

Se construye el caso limite: un "indice dolar" que es EXACTAMENTE el espejo del
EURUSD (correlacion -1,00). Es lo que la gente cree que aporta el DXY llevado al
extremo. Despues se aplica el filtro de confluencia clasico y se cuenta cuantas
operaciones descarta.
"""
import numpy as np, pandas as pd, sys
sys.path.insert(0,"bt")
m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
ch = pd.read_parquet("data/ch_dol.parquet")

# indice dolar espejo perfecto: correlacion -1,00 con EURUSD por construccion
ch["dxy_hi"] = -ch["low"]; ch["dxy_lo"] = -ch["high"]; ch["dxy_cl"] = -ch["close"]

src = open("bt/estrategia_dol.py").read().replace("if d_fav > d_con: continue",
                                                  "if d_fav > 0.5*d_con: continue")
ns={}; exec(compile(src,"m","exec"), ns)
cfg = ns["C"](dol_filtro=True, tp_r=3.0)
sig,_ = ns["senales"](ch, cfg)
print(f"Setups del CRT+DOL sin filtro de DXY: {len(sig)}\n")

# --- el filtro de confluencia que todo el mundo usa ---
# "compro EURUSD solo si el DXY esta haciendo lo contrario"
h4 = ch.groupby("h4_id").agg(e_hi=("high","max"), e_lo=("low","min")).reset_index()
h4["e_p_hi"], h4["e_p_lo"] = h4.e_hi.shift(1), h4.e_lo.shift(1)
mapa = h4.set_index("h4_id")

conf = 0
for s in sig.itertuples():
    fila = ch[ch.ts == s.ts]
    if fila.empty: continue
    k = fila.h4_id.iloc[0]
    if k not in mapa.index: continue
    r = mapa.loc[k]
    if np.isnan(r.e_p_hi): continue
    if s.largo:
        # EURUSD barre su minimo -> el indice espejo barre su maximo
        eur = r.e_lo < r.e_p_lo
        dxy = (-r.e_hi) > (-r.e_p_hi) if False else ((-r.e_lo) > (-r.e_p_lo))
    else:
        eur = r.e_hi > r.e_p_hi
        dxy = ((-r.e_hi) < (-r.e_p_hi))
    if eur and dxy: conf += 1

print("=== FILTRO 'CONFLUENCIA CON EL INDICE DOLAR' ===")
print(f"  setups en que EURUSD barre su extremo Y el indice espejo barre el suyo:")
print(f"  {conf} de {len(sig)}  =  {100*conf/len(sig):.1f}%")
print()
print("  El filtro no descarta NADA, porque no puede: si el indice es el espejo")
print("  del euro, que uno barra su minimo YA IMPLICA que el otro barra su maximo.")
print("  Es la misma frase dicha dos veces.\n")

print("=== CUANTA INFORMACION INDEPENDIENTE TIENE UN ACTIVO SEGUN SU CORRELACION ===")
print(f"{'correlacion':>12s} {'R2':>7s} {'varianza independiente':>24s}")
for c in (-1.00, -0.98, -0.95, -0.90, -0.85, -0.70, -0.50):
    print(f"{c:>12.2f} {c*c:>7.2f} {100*(1-c*c):>23.0f}%")
print()
print("  DXY frente a EURUSD ronda -0,95 -> solo el 10% de su movimiento es")
print("  independiente. Y ese 10% es sobre todo yen y dolar canadiense: ruido")
print("  respecto a lo que le pasa al euro, no informacion.")
print()
print("  GBPUSD frente a EURUSD ronda +0,85 -> un 28% independiente.")
print("  Casi el triple de informacion nueva. Por eso el SMT se hace con la libra.")
