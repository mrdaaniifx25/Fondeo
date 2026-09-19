"""Probabilidad de pasar un reto de fondeo con la ventaja MEDIDA, por simulacion.

Se usa la distribucion real de R neta del modelo, no una aproximacion normal.
Reglas tipicas de un reto de dos fases sobre 10.000 EUR:
   fase 1  objetivo +10 %   fase 2  objetivo +5 %
   perdida maxima total 10 % del saldo inicial
   perdida maxima diaria 5 % del saldo al empezar el dia
"""
import numpy as np, pandas as pd

F = pd.read_parquet("data/barrido_ml_pred.parquet")
D10 = F[F.dec == 10]
ESCEN = {
    "decil superior (pre-registrado)": D10.Rn.to_numpy(),
    "mejor corte medido (stop >=10 p)": D10[D10.rgoP >= 10].Rn.to_numpy(),
    "si el coste bajara a 0,97 pips": (D10[D10.rgoP >= 10].Rb.to_numpy()
                                       - 0.97 / D10[D10.rgoP >= 10].rgoP.to_numpy()),
    "ventaja CERO (moneda al aire)": None,
}
F["Rb"] = 3 * F.gana - 1
D10 = F[F.dec == 10]
ESCEN["mejor corte medido (stop >=10 p)"] = D10[D10.rgoP >= 10].Rn.to_numpy()
ESCEN["si el coste bajara a 0,97 pips"] = (D10[D10.rgoP >= 10].Rb.to_numpy()
                                           - 0.97 / D10[D10.rgoP >= 10].rgoP.to_numpy())

RIESGO, DIA, MAXDIAS = 0.01, 4, 200

def fase(rs, objetivo, rng):
    """Devuelve True si llega al objetivo antes de saltar algun limite."""
    eq = 0.0                       # en fraccion del saldo inicial
    minimo = -0.10                 # perdida maxima total
    for _ in range(MAXDIAS):
        ini = eq
        for _ in range(DIA):
            eq += RIESGO * rs[rng.integers(len(rs))]
            if eq <= minimo: return False
            if eq - ini <= -0.05: return False      # limite diario
            if eq >= objetivo: return True
    return False

def simula(rs, n=20000, semilla=7):
    rng = np.random.default_rng(semilla)
    p1 = sum(fase(rs, 0.10, rng) for _ in range(n)) / n
    p2 = sum(fase(rs, 0.05, rng) for _ in range(n)) / n
    return p1, p2, p1 * p2

print(f"{'escenario':<36}{'R media':>9}{'fase 1':>9}{'fase 2':>9}{'LAS DOS':>10}{'intentos':>10}")
for nom, rs in ESCEN.items():
    if rs is None:
        base = ESCEN["mejor corte medido (stop >=10 p)"]
        rs = base - base.mean()          # misma forma, media cero
    p1, p2, p = simula(rs)
    print(f"{nom:<36}{rs.mean():>+9.4f}{100*p1:>8.1f} %{100*p2:>8.1f} %"
          f"{100*p:>9.1f} %{1/p:>9.1f}")

print("\ny una vez dentro, con la cuenta ya fondeada:")
rs = ESCEN["mejor corte medido (stop >=10 p)"]
rng = np.random.default_rng(11)
n = 20000
viva = sum(fase(rs, 0.075, rng) for _ in range(n)) / n
print(f"  llegar a +7,5 % (los 750 EUR del mes) antes de reventar: {100*viva:.1f} %")
print(f"  repetirlo seis meses seguidos: {100*viva**6:.2f} %")
