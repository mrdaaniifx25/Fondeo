"""¿Que ha valido esto, en dinero?"""
import numpy as np, pandas as pd

print("=== 1. LO QUE HABRIA COSTADO OPERAR LAS TRES ESTRATEGIAS ===")
print("   Cuenta de 100.000 (fondeada tipica), riesgo 1% por operacion\n")
casos = [
    ("Cuatro confirmaciones (video 1)", "data/trades_ls_base.csv", -176.84),
    ("CRT Trade Planner (indicador)",   "data/trades_crt_base.csv", -92.14),
]
total_perdido = 0
for nom, f, rtot in casos:
    try:
        tr = pd.read_csv(f); R = tr.R.to_numpy()
    except Exception:
        continue
    eq = 100000.0; pico = eq; dd = 0
    for r in R:
        eq *= (1+0.01*r); pico=max(pico,eq); dd=max(dd,(pico-eq)/pico)
    print(f"   {nom:34s} {len(R):>5} ops")
    print(f"      capital final {eq:>10,.0f}  ({100*(eq/100000-1):+.1f}%)  maxDD {100*dd:.0f}%")
    total_perdido += 100000-eq
print(f"\n   Perdida combinada si hubieras operado las dos: {total_perdido:>10,.0f} EUR")

print("\n=== 2. EL COSTE REAL DE OPERAR SIN VENTAJA EN RETOS DE FONDEO ===")
tr = pd.read_csv("data/trades_final.csv")
R0 = tr.R.to_numpy() - tr.R.mean()          # misma forma, ventaja cero
def ciclo(Rp, riesgo=0.01, n=20000, cuota=100, semilla=0):
    """Pasa el reto -> opera la fondeada hasta ganar 10% o perderla."""
    rng=np.random.default_rng(semilla)
    gastado=0.0; ganado=0.0
    for _ in range(n):
        gastado += cuota
        eq=1.0
        # fase de reto: +10% o -10%
        for _ in range(400):
            eq*=(1+riesgo*rng.choice(Rp))
            if eq<=0.90: break
            if eq>=1.10:
                # fondeada: mismo sistema hasta +10% (retirada) o -10% (perdida)
                e2=1.0
                for _ in range(400):
                    e2*=(1+riesgo*rng.choice(Rp))
                    if e2<=0.90: break
                    if e2>=1.10: ganado += 0.10*100000*0.8; break
                break
    return gastado/n, ganado/n
for nom, Rp in (("ventaja CERO (las 3 estrategias)", R0),
                ("ventaja medida (CRT+DOL)", tr.R.to_numpy())):
    g, w = ciclo(Rp)
    print(f"   {nom:34s} coste medio {g:>6.0f} EUR | retirada media {w:>7.0f} EUR "
          f"| neto {w-g:>+8.0f} EUR por ciclo")

print("\n=== 3. LO QUE TE CUESTA HOY EL BREAK-EVEN EN +1R ===")
print("   Sobre 54 operaciones al ano, cuenta de 100.000 al 1%:")
for nom, rop in (("sin tocar el stop", 0.1703), ("moviendo a BE en +1R", 0.0175)):
    print(f"   {nom:24s} {rop:+.4f} R/op -> {54*rop*1000:>+8,.0f} EUR al ano")
print(f"   diferencia: {54*(0.1703-0.0175)*1000:>+8,.0f} EUR al ano")
