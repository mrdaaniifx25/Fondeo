"""Familias candidatas. Todas se evaluan SOLO en entrenamiento."""
import numpy as np, pandas as pd
from laboratorio import PIP, barras

def _sesion(m1, h_ini, h_fin):
    """Alto/bajo de una franja horaria UTC por dia, con el instante en que cierra."""
    ts = pd.DatetimeIndex(m1["ts"])
    dentro = (ts.hour >= h_ini) & (ts.hour < h_fin)
    s = m1.loc[dentro].copy(); s["d"] = pd.DatetimeIndex(s["ts"]).normalize()
    g = s.groupby("d").agg(hi=("high","max"), lo=("low","min"), fin=("ts","max"))
    g["listo"] = g["fin"] + pd.Timedelta(minutes=1)
    return g.reset_index()

def _m15(m1):
    return barras(m1, "15min")

# ── A / B · rango de Asia: ruptura o desvanecimiento ────────────────────────
def asia(m1, fade=False, rr=2.0, sl="mid", h_op=(7,11), asia_h=(0,6)):
    g = _sesion(m1, *asia_h)
    ch = _m15(m1); ch["d"] = pd.DatetimeIndex(ch["ts"]).normalize()
    ch = ch.merge(g[["d","hi","lo","listo"]], on="d", how="left").dropna(subset=["hi"])
    ts = pd.DatetimeIndex(ch["ts"])
    ok = (ts.hour >= h_op[0]) & (ts.hour < h_op[1]) & (ch["ts"] >= ch["listo"])
    ch = ch[ok]
    out, visto = [], set()
    for r in ch.itertuples():
        if r.d in visto: continue
        rompe_arriba = r.close > r.hi; rompe_abajo = r.close < r.lo
        if not (rompe_arriba or rompe_abajo): continue
        largo = rompe_arriba if not fade else rompe_abajo
        mid = (r.hi + r.lo)/2
        px = r.close
        s = (mid if sl=="mid" else (r.lo if largo else r.hi))
        if largo and s >= px: continue
        if (not largo) and s <= px: continue
        visto.add(r.d)
        out.append(dict(ts=r.ts + pd.Timedelta(minutes=15), largo=largo,
                        entrada=px, sl=s, rr=rr))
    return pd.DataFrame(out)

# ── C · barrido del maximo/minimo del dia anterior y cierre de vuelta ───────
def pdhl(m1, rr=2.0, buf=1.0, h_op=(7,16)):
    ts = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC").tz_convert("America/New_York")
    dia = pd.Index((ts + pd.Timedelta(hours=7)).date)
    d = m1.copy(); d["k"] = dia
    g = d.groupby("k").agg(hi=("high","max"), lo=("low","min"), fin=("ts","max")).reset_index()
    g["p_hi"], g["p_lo"] = g.hi.shift(1), g.lo.shift(1)
    g["listo"] = g["fin"].shift(1) + pd.Timedelta(minutes=1)
    h1 = barras(m1, "1h"); h1["k"] = pd.Index((pd.DatetimeIndex(h1["ts"]).tz_localize("UTC")
        .tz_convert("America/New_York") + pd.Timedelta(hours=7)).date)
    h1 = h1.merge(g[["k","p_hi","p_lo","listo"]], on="k", how="left").dropna(subset=["p_hi"])
    hh = pd.DatetimeIndex(h1["ts"])
    h1 = h1[(hh.hour >= h_op[0]) & (hh.hour < h_op[1])]
    out, visto = [], set()
    for r in h1.itertuples():
        for largo in (False, True):
            if largo:
                cond = (r.low < r.p_lo) and (r.close > r.p_lo)
                s = r.low - buf*PIP
            else:
                cond = (r.high > r.p_hi) and (r.close < r.p_hi)
                s = r.high + buf*PIP
            if not cond: continue
            key = (r.k, largo)
            if key in visto: continue
            visto.add(key)
            out.append(dict(ts=r.ts + pd.Timedelta(hours=1), largo=largo,
                            entrada=r.close, sl=s, rr=rr))
            break
    return pd.DataFrame(out)

# ── D · ruptura del rango de apertura de Londres ───────────────────────────
def orb(m1, rr=2.0, mins=60, h_ini=7, h_fin=12):
    ch = _m15(m1); ts = pd.DatetimeIndex(ch["ts"])
    ch["d"] = ts.normalize(); ch["h"] = ts.hour; ch["m"] = ts.minute
    ini = ch[(ch.h == h_ini) & (ch.m < mins)]
    g = ini.groupby("d").agg(hi=("high","max"), lo=("low","min")).reset_index()
    ch = ch.merge(g, on="d", how="left").dropna(subset=["hi"])
    mins_abs = ch["h"]*60 + ch["m"]
    ch = ch[(mins_abs >= h_ini*60 + mins) & (ch.h < h_fin)]
    out, visto = [], set()
    for r in ch.itertuples():
        arriba = r.close > r.hi; abajo = r.close < r.lo
        if not (arriba or abajo): continue
        if r.d in visto: continue
        largo = arriba
        s = r.lo if largo else r.hi
        if largo and s >= r.close: continue
        if (not largo) and s <= r.close: continue
        visto.add(r.d)
        out.append(dict(ts=r.ts + pd.Timedelta(minutes=15), largo=largo,
                        entrada=r.close, sl=s, rr=rr))
    return pd.DataFrame(out)

# ── B corregida · fade con stop mas alla de la ruptura ─────────────────────
def asia_fade(m1, rr=2.0, sl_frac=0.5, h_op=(7,11), asia_h=(0,6)):
    g = _sesion(m1, *asia_h)
    ch = _m15(m1); ch["d"] = pd.DatetimeIndex(ch["ts"]).normalize()
    ch = ch.merge(g[["d","hi","lo","listo"]], on="d", how="left").dropna(subset=["hi"])
    ts = pd.DatetimeIndex(ch["ts"])
    ch = ch[(ts.hour>=h_op[0]) & (ts.hour<h_op[1]) & (ch["ts"]>=ch["listo"])]
    out, visto = [], set()
    for r in ch.itertuples():
        rango = r.hi - r.lo
        if rango <= 0: continue
        if r.close > r.hi:   largo, s = False, max(r.high, r.close) + sl_frac*rango
        elif r.close < r.lo: largo, s = True,  min(r.low,  r.close) - sl_frac*rango
        else: continue
        if r.d in visto: continue
        visto.add(r.d)
        out.append(dict(ts=r.ts+pd.Timedelta(minutes=15), largo=largo,
                        entrada=r.close, sl=s, rr=rr))
    return pd.DataFrame(out)

# ── E · deriva horaria: entrar a una hora, salir k horas despues ───────────
def deriva(m1, h_ent=7, horas=6, largo=True, sl_atr=1.5, rr=1.5):
    h1 = barras(m1, "1h")
    tr = pd.concat([h1.high-h1.low, (h1.high-h1.close.shift(1)).abs(),
                    (h1.low-h1.close.shift(1)).abs()], axis=1).max(axis=1)
    h1["atr"] = tr.rolling(24).mean().shift(1)
    hh = pd.DatetimeIndex(h1["ts"])
    s = h1[(hh.hour == h_ent) & h1.atr.notna()]
    out = []
    for r in s.itertuples():
        risk = sl_atr*r.atr
        if risk <= 0: continue
        out.append(dict(ts=r.ts+pd.Timedelta(hours=1), largo=largo,
                        entrada=r.close, sl=r.close-risk if largo else r.close+risk, rr=rr))
    return pd.DataFrame(out)

# ── F · desvanecer la extension diaria ────────────────────────────────────
def ext_fade(m1, k=1.0, rr=1.5, h_op=(10,18)):
    ch = _m15(m1); ts = pd.DatetimeIndex(ch["ts"]); ch["d"] = ts.normalize()
    ap = ch.groupby("d")["open"].first().rename("d_open").reset_index()
    d1 = barras(m1, "1D")
    trr = pd.concat([d1.high-d1.low, (d1.high-d1.close.shift(1)).abs(),
                     (d1.low-d1.close.shift(1)).abs()], axis=1).max(axis=1)
    d1["atr"] = trr.rolling(14).mean().shift(1)
    d1["d"] = pd.DatetimeIndex(d1["ts"]).normalize()
    ch = ch.merge(ap, on="d").merge(d1[["d","atr"]], on="d").dropna(subset=["atr"])
    ts = pd.DatetimeIndex(ch["ts"])
    ch = ch[(ts.hour>=h_op[0]) & (ts.hour<h_op[1])]
    out, visto = [], set()
    for r in ch.itertuples():
        ext = (r.close - r.d_open)/r.atr
        if abs(ext) < k: continue
        if r.d in visto: continue
        largo = ext < 0
        risk = 0.5*r.atr
        visto.add(r.d)
        out.append(dict(ts=r.ts+pd.Timedelta(minutes=15), largo=largo, entrada=r.close,
                        sl=r.close-risk if largo else r.close+risk, rr=rr))
    return pd.DataFrame(out)

# ── G · ruptura por compresion: ORB solo si el rango es estrecho ───────────
def orb_compr(m1, rr=2.0, mins=60, max_ratio=0.6, h_ini=7, h_fin=12):
    ch = _m15(m1); ts = pd.DatetimeIndex(ch["ts"])
    ch["d"]=ts.normalize(); ch["h"]=ts.hour; ch["m"]=ts.minute
    ini = ch[(ch.h==h_ini)&(ch.m<mins)]
    g = ini.groupby("d").agg(hi=("high","max"), lo=("low","min")).reset_index()
    d1 = barras(m1, "1D")
    trr = pd.concat([d1.high-d1.low, (d1.high-d1.close.shift(1)).abs(),
                     (d1.low-d1.close.shift(1)).abs()], axis=1).max(axis=1)
    d1["atr"]=trr.rolling(14).mean().shift(1); d1["d"]=pd.DatetimeIndex(d1["ts"]).normalize()
    g = g.merge(d1[["d","atr"]], on="d").dropna()
    g = g[(g.hi-g.lo) <= max_ratio*g.atr]
    ch = ch.merge(g[["d","hi","lo"]], on="d", how="inner")
    ma = ch["h"]*60+ch["m"]
    ch = ch[(ma >= h_ini*60+mins) & (ch.h < h_fin)]
    out, visto = [], set()
    for r in ch.itertuples():
        arriba = r.close > r.hi; abajo = r.close < r.lo
        if not (arriba or abajo) or r.d in visto: continue
        largo = arriba; s = r.lo if largo else r.hi
        if largo and s>=r.close: continue
        if (not largo) and s<=r.close: continue
        visto.add(r.d)
        out.append(dict(ts=r.ts+pd.Timedelta(minutes=15), largo=largo,
                        entrada=r.close, sl=s, rr=rr))
    return pd.DataFrame(out)
