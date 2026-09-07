"""El reto de FundingPips con la estrategia del oro al COSTE REAL medido.

2026-09: el usuario mide el spread del XAUUSD en FundingPips MT5 y da
0,08-0,20 $. La especificacion asumia 0,20, o sea su peor caso. Aqui se corre
el reto con 0,14 (el punto medio) y se compara con 0,20.

Monte Carlo remuestreando DIAS ENTEROS con reemplazo, no operaciones sueltas:
dentro de un dia estan correlacionadas.

  python3 bt/sqx_reto.py
"""
import numpy as np, pandas as pd

CUENTA = 10_000
OBJ1, OBJ2 = 0.08, 0.05
LIM_DIA, LIM_TOT = 0.05, 0.10
DIAS_MAX, DIAS_MIN, N = 60, 3, 20_000


def dias_de(csv):
    """Cada dia = pares (peor flotante, resultado cerrado) en fraccion del capital.

    El peor flotante hace falta porque el limite diario de una prop firm mira
    el EQUITY con la posicion abierta, no la operacion cerrada.
    """
    O = pd.read_csv(csv)
    prev = O.capital - O.neto
    O["r"] = O.neto / prev
    O["rp"] = O.peor / prev
    O["d"] = pd.to_datetime(O.entrada).dt.date
    por = {k: g[["rp", "r"]].to_numpy() for k, g in O.groupby("d")}
    # TODOS los dias habiles del periodo, no solo los que tuvieron operacion.
    # La estrategia opera ~4 de cada 10 dias; remuestrear solo los activos
    # metia 60 dias con trade en una fase de 60 dias de calendario.
    cal = pd.bdate_range(min(por), max(por)).date
    vacio = np.zeros((0, 2))
    return [por.get(d, vacio) for d in cal], O


def fase(dias, k, objetivo, rng, rr):
    """k = multiplicador de riesgo sobre el tamano original de la estrategia."""
    saldo = 1.0
    for d in range(DIAS_MAX):
        ini = saldo
        for rp, r in dias[rr[d % len(rr)]]:
            flot = saldo * (1 + rp * k)          # equity con la posicion abierta
            if flot <= 1 - LIM_TOT or flot <= ini - LIM_DIA:
                return "revienta"
            saldo *= (1 + r * k)
            if saldo <= 1 - LIM_TOT or saldo <= ini - LIM_DIA:
                return "revienta"
        if saldo >= 1 + objetivo and d + 1 >= DIAS_MIN:
            return "pasa"
    return "tiempo"


if __name__ == "__main__":
    import sys
    suf = sys.argv[1] if len(sys.argv) > 1 else ""
    dias, O = dias_de(f"data/sqx_xauusd_operaciones{suf}.csv")
    esc = float(np.mean([np.abs(d[:, 1]).mean() for d in dias if len(d)]))
    act = sum(1 for d in dias if len(d))
    print(f"=== RETO FUNDINGPIPS · estrategia del oro · {len(O)} operaciones ===")
    print(f"    {len(dias)} dias habiles del periodo, {act} con operacion "
          f"({act/len(dias):.0%}); los demas entran como dias en blanco")
    print(f"    riesgo original de la especificacion: {esc:.2%} de media por operacion\n")
    rng = np.random.default_rng(7)
    print(f"    {'riesgo/op':>10} {'vol anual':>10} {'fase 1':>8} {'fase 2':>8} "
          f"{'LAS DOS':>9} {'vs azar 36,9 %':>15}")
    for k, et in ((0.5, None), (1.0, None), (1.5, None), (2.0, None), (3.0, None)):
        r1 = rng.integers(0, len(dias), (N, DIAS_MAX))
        r2 = rng.integers(0, len(dias), (N, DIAS_MAX))
        p1 = np.array([fase(dias, k, OBJ1, rng, r1[i]) == "pasa" for i in range(N)])
        p2 = np.array([fase(dias, k, OBJ2, rng, r2[i]) == "pasa" for i in range(N)])
        # la fase 2 solo la juegan los que pasaron la 1
        f1, f2 = p1.mean(), p2.mean()
        vol = float(np.std([d[:, 1].sum() * k for d in dias])) * np.sqrt(252)
        print(f"    {esc*k:>9.1%} {vol:>10.1%} {f1:>8.1%} {f2:>8.1%} {f1*f2:>9.1%} "
              f"{(f1*f2-0.369)*100:>+14.1f} pp")
    print("\n    (azar 36,9 % = el techo de la geometria de barreras sin ninguna ventaja,")
    print("     de RESULTADOS_cfd_fondeo.md)")
