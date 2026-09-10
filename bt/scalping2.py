"""La cifra que zanja: ¿cuanta reversion hay REALMENTE, en pips, y cuanto cuesta
acceder a ella? Y despues, backtests de scalping de verdad para confirmarlo."""
import numpy as np, pandas as pd
from math import sqrt, erf
import sys; sys.path.insert(0,"bt")
from laboratorio import Motor, resumen

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
PIP=0.0001; COSTE=1.2

print("=== LA REVERSION EXISTE. ¿CUANTO VALE EN PIPS? ===")
base = np.log(m1.set_index("ts").close.resample("1min").last().dropna()).diff().dropna()
v1 = base.var()
print(f"{'ventana':>9s} {'VR':>8s} {'mov medio':>11s} {'reversion capturable':>21s} {'coste':>7s} {'veredicto':>12s}")
for q in (5, 15, 30, 60):
    agg = base.rolling(q).sum().dropna()[::q]
    vr = agg.var()/(q*v1)
    s = m1.set_index("ts").close.resample(f"{q}min").last().dropna()
    mov = (s.diff().abs()/PIP).mean()
    # el movimiento real es sqrt(VR) veces el de un paseo aleatorio:
    # lo "revertido" es la diferencia entre ambos
    revertido = mov * (1/sqrt(vr) - 1)
    print(f"{q:>6d} min {vr:>8.4f} {mov:>10.2f}p {revertido:>20.2f}p {COSTE:>6.1f}p "
          f"{'RENTABLE' if revertido>COSTE else 'NO LLEGA':>12s}")

print("\n  Traduccion: la reversion es estadisticamente rotunda (z de -15 a -19)")
print("  pero vale decimas de pip. El coste de acceder a ella es 1,2 pips.")
print("  No es una ineficiencia del mercado: ES el spread visto desde fuera.\n")

# ── backtests de scalping reales ───────────────────────────────────────────
def m(regla):
    return m1.set_index("ts").resample(regla, label="left", closed="left").agg(
        open=("open","first"), high=("high","max"), low=("low","min"),
        close=("close","last")).dropna().reset_index()

def fade_mov(ch, k_pips, sl_pips, rr, paso):
    """Tras un movimiento de k pips en una vela, tomar la contraria."""
    o,c = ch.open.to_numpy(), ch.close.to_numpy(); ts = ch.ts.to_numpy()
    mv = (c-o)/PIP
    out=[]
    for i in range(len(ch)-1):
        if abs(mv[i]) < k_pips: continue
        largo = mv[i] < 0
        e = c[i]
        s = e - sl_pips*PIP if largo else e + sl_pips*PIP
        out.append(dict(ts=pd.Timestamp(ts[i])+pd.Timedelta(minutes=paso),
                        largo=largo, entrada=e, sl=s, rr=rr))
    return pd.DataFrame(out)

def zscore_rev(ch, n, z_umbral, sl_pips, rr, paso):
    c = ch.close
    mu, sd = c.rolling(n).mean(), c.rolling(n).std()
    z = ((c-mu)/sd).to_numpy(); ts = ch.ts.to_numpy(); cv = c.to_numpy()
    out=[]
    for i in range(n, len(ch)-1):
        if np.isnan(z[i]) or abs(z[i]) < z_umbral: continue
        largo = z[i] < 0
        e = cv[i]; s = e - sl_pips*PIP if largo else e + sl_pips*PIP
        out.append(dict(ts=pd.Timestamp(ts[i])+pd.Timedelta(minutes=paso),
                        largo=largo, entrada=e, sl=s, rr=rr))
    return pd.DataFrame(out)

mo = Motor(m1)
print("=== BACKTESTS DE SCALPING (muestra completa 2020-2026) ===")
print(f"{'estrategia':44s} {'n':>7s} {'WR':>6s} {'bruto/op':>9s} {'p':>7s} {'R neto':>9s} {'PF':>6s}")
print("-"*94)
pruebas=[]
for paso, regla in ((1,"1min"), (5,"5min")):
    ch = m(regla)
    for k in (3,5,8):
        for sl,rr in ((3,1.0),(5,1.0),(5,2.0)):
            pruebas.append((f"fade mov>{k}p en M{paso}, SL{sl} RR{rr}",
                            fade_mov(ch,k,sl,rr,paso)))
    for n,zu in ((20,2.0),(50,2.5)):
        for sl,rr in ((4,1.0),(6,1.5)):
            pruebas.append((f"z-score {n} |z|>{zu} en M{paso}, SL{sl} RR{rr}",
                            zscore_rev(ch,n,zu,sl,rr,paso)))
for nom, sig in pruebas:
    if sig.empty or len(sig)<100: continue
    tr = mo.resolver(sig, horas=8)
    r = resumen(tr, nom)
    if r is None: continue
    print(f"{nom:44s} {r['n']:>7d} {r['wr']:>5.1f}% {r['bruto']:>+9.4f} {r['p']:>7.3f} "
          f"{r['Rneto']:>+9.1f} {r['pf']:>6.3f}")
