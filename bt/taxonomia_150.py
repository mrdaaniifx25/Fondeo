"""Que son las 115 entradas que NO estan sobre una vela que toca el nivel.

La primera pasada solo caracterizo el 23 % mas llamativo -el rechazo del nivel-
y construyo la regla con eso. Esto mira el resto.

  python3 bt/taxonomia_150.py
"""
import json, numpy as np, pandas as pd
U, TZ, INI, FIN = 1e-4, "Europe/Madrid", 480, 690

t = pd.read_csv("data/contexto_suyas.csv"); t["dia"] = pd.to_datetime(t.dia).dt.date
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
m1 = m1[m1.dia.isin(set(t.dia))].reset_index(drop=True)

fil = []
for r in t.itertuples():
    d1 = m1[m1.dia == r.dia]
    a  = d1[d1["min"] < INI]
    hi, lo = float(a.high.max()), float(a.low.min())
    ses = d1[(d1["min"] >= INI) & (d1["min"] < r.ent_min)]
    if len(ses) < 5: continue
    smax, smin = float(ses.high.max()), float(ses.low.min())
    # los 15 minutos anteriores a su entrada, en M1
    v15 = d1[(d1["min"] >= r.ent_min-15) & (d1["min"] < r.ent_min)]
    if len(v15) < 5: continue
    imp = (float(v15.close.iloc[-1]) - float(v15.open.iloc[0]))/U
    # extremo del que sale su stop
    ext = float(v15.low.min()) if r.lado > 0 else float(v15.high.max())
    fil.append(dict(
        toca=bool(r.toca), mecha=bool(r.mecha), fuera=bool(r.cuerpo_fuera), R=r.R, mot=r.mot,
        dentro_asia=bool(lo <= r.ent <= hi),
        d_asia_alto=(hi - r.ent)/U, d_asia_bajo=(r.ent - lo)/U,
        d_max_ses=(smax - r.ent)/U, d_min_ses=(smin - r.ent)/U,
        cerca_ses=min(abs(smax-r.ent), abs(smin-r.ent))/U,
        # ¿compra cerca del minimo de la sesion o cerca del maximo?
        en_extremo=("bajo" if abs(r.ent-smin) < abs(r.ent-smax) else "alto"),
        imp15=imp, a_favor_imp=bool(np.sign(imp) == r.lado),
        lado=r.lado, hora=r.hora, cerca=r.cerca))
D = pd.DataFrame(fil)
print(f"{len(D)} de 150 con contexto completo\n")

print("="*74); print("TAXONOMÍA · en qué se apoya cada entrada"); print("="*74)
D["clase"] = np.where(D.mecha, "rechazo del nivel de Asia",
             np.where(D.fuera, "rotura del nivel de Asia",
             np.where(D.cerca_ses <= 3, "extremo de la sesión (no de Asia)",
             np.where(D.dentro_asia, "dentro del rango de Asia, sin nivel cerca",
                      "fuera del rango de Asia, sin nivel cerca"))))
for c, s in D.groupby("clase"):
    r = s[s.mot.isin(["TP","SL"])]
    print(f"  {c:42s} {len(s):3d} ({100*len(s)/len(D):4.1f} %)  "
          f"acierto {100*(r.mot=='TP').mean():5.1f} %")

print("\n" + "="*74); print("¿VA A FAVOR O EN CONTRA DEL IMPULSO DE LOS 15 MINUTOS ANTERIORES?")
print("="*74)
for v, nom in ((True, "a favor del impulso"), (False, "EN CONTRA del impulso")):
    s = D[D.a_favor_imp == v]; r = s[s.mot.isin(["TP","SL"])]
    print(f"  {nom:24s} {len(s):3d} ({100*len(s)/len(D):4.1f} %)  "
          f"acierto {100*(r.mot=='TP').mean():5.1f} %  ·  impulso mediano "
          f"{s.imp15.abs().median():.1f} p")

print("\n" + "="*74); print("¿DÓNDE ESTÁ EL PRECIO EN LA SESIÓN CUANDO ENTRA?"); print("="*74)
print(f"  distancia mediana al máximo de la sesión: {D.d_max_ses.median():.1f} p")
print(f"  distancia mediana al mínimo de la sesión: {D.d_min_ses.median():.1f} p")
for lado, nom in ((1,"COMPRAS"), (-1,"VENTAS")):
    s = D[D.lado == lado]
    cerca_min = (s.cerca_ses == s.d_min_ses.abs())
    print(f"  {nom}: {len(s):3d}  ·  entra más cerca del "
          f"{'mínimo' if (s.en_extremo=='bajo').mean()>0.5 else 'máximo'} de la sesión en el "
          f"{100*max((s.en_extremo=='bajo').mean(), (s.en_extremo=='alto').mean()):.0f} % de los casos")
    r = s[s.mot.isin(["TP","SL"])]
    for e in ("bajo","alto"):
        ss = s[s.en_extremo == e]; rr = ss[ss.mot.isin(["TP","SL"])]
        if len(rr): print(f"      pegado al {e:5s} de la sesión: {len(ss):3d}  "
                          f"acierto {100*(rr.mot=='TP').mean():5.1f} %")
D.to_csv("data/taxonomia_150.csv", index=False)
