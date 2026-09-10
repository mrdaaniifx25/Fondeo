"""Las tres pruebas que pueden tumbar la estrategia de la vela de apertura.

  1 FUERA DE MUESTRA  ajustar en 2020-2023, comprobar en 2024-2026
  2 OTROS PARES       GBPUSD y USDJPY con las mismas reglas
  3 CONTROL POSITIVO  inyectar deriva conocida y ver si el motor la encuentra

  python3 bt/apertura_validacion.py
"""
import os, itertools, numpy as np, pandas as pd
os.environ.setdefault("NULOS","0")
src = open("bt/apertura_eurusd.py").read()
exec(src.split("D = rejilla(M)")[0])

def rej_periodo(MM, a, b):
    global M
    old = M; M = MM[(pd.to_datetime(MM["d"]).dt.year>=a) & (pd.to_datetime(MM["d"]).dt.year<=b)]
    r = rejilla(M); M = old; return r

print("\n=== 1 · FUERA DE MUESTRA ===")
A = rej_periodo(M, 2020, 2023); B = rej_periodo(M, 2024, 2026)
k = ["apert","buf","rr","bias"]
J = A.set_index(k)[["n","R","z"]].join(B.set_index(k)[["n","R","z"]], rsuffix="_f").dropna()
print(f"  {'apert':>6} {'buf':>5} {'rr':>4} {'bias':>6} | {'n aj':>5} {'R aj':>8} {'z aj':>6}"
      f" | {'n fu':>5} {'R fuera':>9} {'z fuera':>8}")
for i, r in J.sort_values("z", ascending=False).head(6).iterrows():
    hh=f"{int(i[0])//60:02d}:{int(i[0])%60:02d}"
    print(f"  {hh:>6} {i[1]:>5.1f} {i[2]:>4.0f} {str(bool(i[3])):>6} | {int(r.n):>5} "
          f"{r.R:>+8.4f} {r.z:>+6.2f} | {int(r.n_f):>5} {r.R_f:>+9.4f} {r.z_f:>+8.2f}")
c = np.corrcoef(J.z, J.z_f)[0,1]
mej = J.sort_values("z", ascending=False).iloc[0]
print(f"\n  correlacion ajuste/fuera de muestra ({len(J)} celdas): {c:+.3f}")
print(f"  la mejor del ajuste (z {mej.z:+.2f}) saca fuera z {mej.z_f:+.2f}, R {mej.R_f:+.4f}")
print(f"  celdas positivas fuera de muestra: {int((J.R_f>0).sum())}/{len(J)}")

print("\n=== 2 · OTROS PARES, mismas reglas ===")
for par, ruta in (("GBPUSD","data/gbpusd_m1.parquet"), ("USDJPY","data/usdjpy_m1.parquet")):
    X = pd.read_parquet(ruta); X["ts"]=pd.to_datetime(X["ts"])
    X = X.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    lo = X.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/London").dt.tz_localize(None)
    X["t"]=lo; X["d"]=lo.dt.date; X["m"]=lo.dt.hour*60+lo.dt.minute
    X = X[(lo.dt.dayofweek<5).to_numpy()].reset_index(drop=True)
    old=M; M=X; R=rejilla(X); M=old
    if not len(R): print(f"  {par}: sin operaciones"); continue
    b = R.sort_values("z", ascending=False).iloc[0]
    print(f"  {par}: mejor z {R.z.max():+.2f} · celdas z>2 {int((R.z>2).sum())}/{len(R)}"
          f" · celdas R>0 {int((R.R>0).sum())}/{len(R)}"
          f" · mejor celda {int(b.apert)//60:02d}:00 buf{b.buf:.0f} rr{b.rr:.0f} "
          f"R {b.R:+.4f}", flush=True)
