"""Genera el grafico M1 de un dia con los niveles de Asia y su entrada."""
import sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

TZ, INI, FIN = "Europe/Madrid", 480, 690
TINTA, TINTA2, TINTA3 = "#12161c", "#4e5864", "#8b95a1"
SUBE, BAJA, LINEA = "#0ca30c", "#d03b3b", "#dde3ea"
ASIA, ENTRADA = "#2a78d6", "#eb6834"

d = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
               pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").drop_duplicates("ts")
loc = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
d["dia"] = loc.date; d["min"] = loc.hour*60+loc.minute; d["hm"] = loc.strftime("%H:%M")

def dibuja(fecha, h_ent, lado_ent, desde=420, hasta=700, salida=None):
    g = d[d.dia == pd.Timestamp(fecha).date()].reset_index(drop=True)
    m = g["min"].to_numpy()
    asia = g[m < INI]
    aHi, aLo = asia.high.max(), asia.low.min()
    v = g[(m >= desde) & (m <= hasta)].reset_index(drop=True)
    O,H,L,C = (v.open.to_numpy(), v.high.to_numpy(), v.low.to_numpy(), v.close.to_numpy())
    hm, mm = v.hm.to_numpy(), v["min"].to_numpy()
    x = np.arange(len(v))

    fig, ax = plt.subplots(figsize=(16, 9), dpi=110)
    fig.patch.set_facecolor("#fdfdfe"); ax.set_facecolor("#fdfdfe")

    # ventana operativa sombreada
    dentro = np.flatnonzero((mm >= INI) & (mm <= FIN))
    if len(dentro):
        ax.axvspan(dentro[0], dentro[-1], color=ASIA, alpha=.05, zorder=0)
        ax.text(dentro[0]+3, ax.get_ylim()[0], "", fontsize=1)

    # velas
    for i in range(len(v)):
        col = SUBE if C[i] >= O[i] else BAJA
        ax.plot([i, i], [L[i], H[i]], color=col, lw=.8, zorder=2, solid_capstyle="butt")
        ax.add_patch(Rectangle((i-.34, min(O[i],C[i])), .68,
                     max(abs(C[i]-O[i]), 1e-6), facecolor=col, edgecolor=col,
                     lw=.4, zorder=3))

    # niveles de Asia
    for niv, txt in ((aHi, f"máximo de Asia  {aHi:.5f}"), (aLo, f"mínimo de Asia  {aLo:.5f}")):
        if L.min()-3e-4 <= niv <= H.max()+3e-4:
            ax.axhline(niv, color=ASIA, lw=1.6, zorder=4)
            ax.text(len(v)-1, niv, "  "+txt, color=ASIA, fontsize=11,
                    va="center", ha="left", fontweight="600")

    # rotura de Asia
    for niv, cmp_, nom in ((aHi, H > aHi, "rompe el máximo"), (aLo, L < aLo, "rompe el mínimo")):
        idx = np.flatnonzero(cmp_ & (mm >= INI))
        if len(idx):
            i = int(idx[0])
            ax.axvline(i, color=ASIA, lw=1, ls=(0,(4,3)), alpha=.8, zorder=1)
            ax.text(i, H.max(), f" {nom}\n {hm[i]}", color=ASIA, fontsize=10,
                    va="top", ha="left", fontweight="600")

    # su entrada
    if h_ent:
        j = np.flatnonzero(hm == h_ent)
        if len(j):
            j = int(j[0])
            ax.axvline(j, color=ENTRADA, lw=1.6, zorder=5)
            ax.scatter([j], [C[j]], s=170, marker="o", facecolor="#fdfdfe",
                       edgecolor=ENTRADA, lw=2.4, zorder=6)
            ax.annotate(f"TU {lado_ent.upper()}\n{h_ent} · {C[j]:.5f}",
                        xy=(j, C[j]), xytext=(j+9, C[j] - (H.max()-L.min())*.16),
                        color=ENTRADA, fontsize=12, fontweight="700", ha="left",
                        arrowprops=dict(arrowstyle="-", color=ENTRADA, lw=1.4))

    paso = 15
    tk = [i for i in range(len(v)) if mm[i] % paso == 0]
    ax.set_xticks(tk); ax.set_xticklabels([hm[i] for i in tk], fontsize=10, color=TINTA2)
    ax.tick_params(axis="y", labelsize=10, colors=TINTA2)
    ax.yaxis.set_major_formatter(lambda y, p: f"{y:.5f}")
    ax.grid(axis="y", color=LINEA, lw=.7, zorder=0)
    for s in ("top","right","left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(LINEA)
    ax.set_xlim(-1, len(v)+16)
    ax.set_title(f"EURUSD · M1 · {fecha}   (hora de Madrid)",
                 fontsize=15, fontweight="700", color=TINTA, loc="left", pad=14)
    ax.text(0, 1.005, "sombreado = tu ventana de 08:00 a 11:30",
            transform=ax.transAxes, fontsize=10.5, color=TINTA3, va="bottom")
    fig.tight_layout()
    fig.savefig(salida, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  {salida}   Asia {aLo:.5f} - {aHi:.5f}")

SAL = "/tmp/claude-0/-home-user-Fondeo/0d8c92b4-16e7-53a1-886b-22385a3d6383/scratchpad/"
dibuja("2026-08-14", "09:40", "compra", salida=SAL+"dia_14ago.png")
dibuja("2026-08-17", "08:30", "compra", salida=SAL+"dia_17ago.png")
dibuja("2026-08-04", "09:30", "venta",  salida=SAL+"dia_04ago.png")
