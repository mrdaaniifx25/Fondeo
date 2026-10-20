"""Extrae dias completos para el artefacto: lo que la estrategia marcaria y
lo que NO, con el motivo de cada descarte.

  python3 bt/extrae_dias.py
"""
import numpy as np, pandas as pd, json

U, COSTE, KATR, RR, HOR = 1e-4, 0.70, 1.5, 2.0, 6*60
M = pd.read_parquet("data/eurusd_m1.parquet")
M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
loc = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
M["dia"] = loc.dt.floor("D"); M["h"] = loc.dt.hour + loc.dt.minute/60.0
HH, LL, OO = M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy()

g = M.assign(k=loc.dt.floor("15min")).groupby("k", sort=True)
b = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
          fin=("high", lambda x: x.index[-1]))
b = b[b.index.notna()]
tr = pd.concat([b.h-b.l,(b.h-b.c.shift(1)).abs(),(b.l-b.c.shift(1)).abs()],axis=1).max(axis=1)
b["atr"] = tr.rolling(14).mean().shift(1)
B = b.index; hb = B.hour + B.minute/60.0
O15,H15,L15,C15,A15 = (b[k].to_numpy() for k in ("o","h","l","c","atr"))
FIN = b.fin.to_numpy().astype(int)
asia = M[(M.h>=0)&(M.h<8)].groupby("dia").agg(ah=("high","max"), al=("low","min"))

def resuelve(e, lado, rgo, rec):
    ent=OO[e]; sl=ent-lado*rgo; tp=ent+lado*rec
    a,z=e,min(e+HOR,len(M)); hh,ll=HH[a:z],LL[a:z]
    if lado>0: ks=np.nonzero(ll<=sl)[0]; kt=np.nonzero(hh>=tp)[0]
    else:      ks=np.nonzero(hh>=sl)[0]; kt=np.nonzero(ll<=tp)[0]
    fs=ks[0] if len(ks) else 10**9; ft=kt[0] if len(kt) else 10**9
    if ft<fs: return rec/rgo, "objetivo", int(ft)
    if fs<10**9: return -1.0, "stop", int(fs)
    k=min(e+HOR,len(M))-1
    return (M.close.to_numpy()[k]-ent)*lado/rgo, "tiempo", HOR

dias = sorted(set(pd.Series(B).dt.floor("D")))
casos = []
for d in dias:
    if d not in asia.index: continue
    ah, al = asia.loc[d,"ah"], asia.loc[d,"al"]
    if not (np.isfinite(ah) and np.isfinite(al)): continue
    sel = np.nonzero((pd.Series(B).dt.floor("D")==d).to_numpy() & (hb>=6) & (hb<15))[0]
    if len(sel) < 20: continue
    velas = [{"t": B[i].strftime("%H:%M"), "o": round(O15[i],5), "h": round(H15[i],5),
              "l": round(L15[i],5), "c": round(C15[i],5),
              "v": bool(8 <= hb[i] < 11)} for i in sel]
    marcas, op, hechos = [], None, set()
    for n_, i in enumerate(sel):
        if not (8 <= hb[i] < 11): continue
        tocaAlto = H15[i] >= ah; tocaBajo = L15[i] <= al
        if not (tocaAlto or tocaBajo): continue
        lado, razon = 0, ""
        if tocaAlto and tocaBajo:  razon = "barre los DOS lados"
        elif tocaAlto:
            if C15[i] >= ah: razon = "barre arriba pero CIERRA FUERA"
            else:            lado = -1
        else:
            if C15[i] <= al: razon = "barre abajo pero CIERRA FUERA"
            else:            lado = 1
        if lado != 0 and lado in hechos: razon, lado = "ya hubo señal de ese lado hoy", 0
        if lado != 0 and len(hechos) >= 3: razon, lado = "tope de 3 al día", 0
        if lado != 0 and (not np.isfinite(A15[i]) or A15[i] <= 0): razon, lado = "sin ATR", 0
        if lado == 0:
            marcas.append({"i": n_, "tipo": "no", "razon": razon}); continue
        hechos.add(lado)
        e = FIN[i]+1
        if e >= len(M): continue
        ent = OO[e]; rgo = KATR*A15[i]; rec = RR*rgo
        R, fin, mins = resuelve(e, lado, rgo, rec)
        marcas.append({"i": n_, "tipo": "si", "lado": int(lado),
            "ent": round(ent,5), "sl": round(ent-lado*rgo,5), "tp": round(ent+lado*rec,5),
            "pips": round(rgo/U,1), "lotes": round(50/(rgo*100000),2),
            "R": round(R,2), "neta": round(R-COSTE/(rgo/U),3), "fin": fin,
            "horas": round(mins/60,1)})
        if op is None: op = marcas[-1]
    casos.append({"d": d.strftime("%Y-%m-%d"), "dow": "LMXJV"[d.weekday()] if d.weekday()<5 else "-",
                  "ah": round(ah,5), "al": round(al,5),
                  "rango": round((ah-al)/U,1), "velas": velas, "marcas": marcas,
                  "ops": sum(1 for m in marcas if m["tipo"]=="si"),
                  "R": round(sum(m["neta"] for m in marcas if m["tipo"]=="si"),3)})

con = [c for c in casos if c["ops"] > 0]
sin = [c for c in casos if c["ops"] == 0 and c["marcas"]]
nada = [c for c in casos if not c["marcas"]]
print(f"días totales {len(casos)}  ·  con señal {len(con)}  ·  "
      f"barrido sin señal {len(sin)}  ·  sin barrido {len(nada)}")
tot = [m for c in casos for m in c["marcas"] if m["tipo"]=="si"]
print(f"operaciones {len(tot)}  ·  acierto {100*np.mean([t['R']>0 for t in tot]):.1f} %  ·  "
      f"R neta media {np.mean([t['neta'] for t in tot]):+.4f}")
rng = np.random.default_rng(3)
gan = [c for c in con if c["R"] > 0]; per = [c for c in con if c["R"] <= 0]
sel = (list(rng.choice(gan, size=min(22,len(gan)), replace=False)) +
       list(rng.choice(per, size=min(22,len(per)), replace=False)) +
       list(rng.choice(sin, size=min(12,len(sin)), replace=False)) +
       list(rng.choice(nada, size=min(6,len(nada)), replace=False)))
sel = sorted(sel, key=lambda c: c["d"])
res = {"n": len(tot), "acierto": round(100*float(np.mean([t['R']>0 for t in tot])),1),
       "neta": round(float(np.mean([t['neta'] for t in tot])),4),
       "dias": len(casos), "conSenal": len(con), "sinSenal": len(sin), "sinBarrido": len(nada),
       "casos": sel}
json.dump(res, open("data/dias_artefacto.json","w"), ensure_ascii=False)
print(f"casos en el artefacto: {len(sel)}  ·  "
      f"{len(open('data/dias_artefacto.json').read())/1024:.0f} KB")
