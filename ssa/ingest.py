"""Download (with caching), validate and load football-data.co.uk CSVs into SQLite.
Never fabricates: missing values stay NULL and are reported as unavailable."""
import io, json, sqlite3, hashlib, datetime as dt
import numpy as np, pandas as pd, requests
from .config import *

NOW = lambda: dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def _targets():
    for s in SEASONS:
        for l in MAIN_LEAGUES:
            yield f"{l}_{s}.csv", f"{BASE}/mmz4281/{s}/{l}.csv"
    for c in EXTRA:
        yield f"X_{c}.csv", f"{BASE}/new/{c}.csv"
    yield "fixtures.csv", f"{BASE}/fixtures.csv"

def download(force=False, max_age_h=12):
    """Cache: skip files younger than max_age_h unless force. Records HTTP Last-Modified + fetch time."""
    RAW.mkdir(parents=True, exist_ok=True)
    meta_p = RAW / "_meta.json"
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
    for fn, url in _targets():
        p = RAW / fn
        if p.exists() and not force and fn in meta:
            age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(meta[fn]["fetched_at"])).total_seconds()
            if age < max_age_h * 3600:
                continue
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            if not r.content.lstrip(b"\xef\xbb\xbf").startswith((b"Div", b"Country")):
                raise ValueError("not a football-data CSV")
            p.write_bytes(r.content)
            meta[fn] = {"url": url, "final_url": r.url, "fetched_at": NOW(),
                        "last_modified": r.headers.get("Last-Modified"), "sha1": hashlib.sha1(r.content).hexdigest()}
        except Exception as e:
            meta.setdefault(fn, {"url": url})["error"] = f"{type(e).__name__}: {e}"
            print("download failed", fn, e)
    # sanity: detect the RSA->USA redirect class of problem (identical content under different names)
    meta_p.write_text(json.dumps(meta, indent=1))
    return meta

def _read(p):
    for enc in ("utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(p, encoding=enc, on_bad_lines="skip")
            df.columns = [c.replace("\ufeff", "").replace("ï»¿", "").strip() for c in df.columns]
            return df.dropna(axis=1, how="all")
        except UnicodeDecodeError:
            continue

def _num(df, c):
    return pd.to_numeric(df[c], errors="coerce") if c in df else np.nan

def _first(df, cols):
    for c in cols:
        if c in df and pd.to_numeric(df[c], errors="coerce").notna().any():
            return pd.to_numeric(df[c], errors="coerce")
    return pd.Series(np.nan, index=df.index)

def normalize_main(df, league, season, fn):
    o = pd.DataFrame({"league": league, "season": f"20{season[:2]}-{season[2:]}",
        "date": pd.to_datetime(df["Date"], dayfirst=True, format="mixed", errors="coerce"),
        "time": df.get("Time"), "home": df["HomeTeam"], "away": df["AwayTeam"],
        "hg": _num(df, "FTHG"), "ag": _num(df, "FTAG"), "hs": _num(df, "HS"), "as_": _num(df, "AS"),
        "hst": _num(df, "HST"), "ast": _num(df, "AST")})
    for k, cols in {"oh": ["AvgH", "BbAvH", "B365H"], "od": ["AvgD", "BbAvD", "B365D"], "oa": ["AvgA", "BbAvA", "B365A"],
                    "ch": ["PSCH", "AvgCH", "B365CH"], "cd": ["PSCD", "AvgCD", "B365CD"], "ca": ["PSCA", "AvgCA", "B365CA"],
                    "o25": ["Avg>2.5", "BbAv>2.5"], "u25": ["Avg<2.5", "BbAv<2.5"]}.items():
        o[k] = _first(df, cols)
    o["source_file"] = fn
    return o

def normalize_extra(df, code, fn):
    o = pd.DataFrame({"league": code, "season": df["Season"].astype(str),
        "date": pd.to_datetime(df["Date"], dayfirst=True, format="mixed", errors="coerce"),
        "time": df.get("Time"), "home": df["Home"], "away": df["Away"],
        "hg": _num(df, "HG"), "ag": _num(df, "AG")})
    for c in ["hs", "as_", "hst", "ast", "oh", "od", "oa", "o25", "u25"]:
        o[c] = np.nan  # not provided in extra-league files -> unavailable
    o["ch"] = _first(df, ["PSCH", "AvgCH", "B365CH"]); o["cd"] = _first(df, ["PSCD", "AvgCD", "B365CD"]); o["ca"] = _first(df, ["PSCA", "AvgCA", "B365CA"])
    o["source_file"] = fn
    return o

def validate(o):
    """Drop rows that fail hard checks; report counts."""
    n0 = len(o)
    o = o.dropna(subset=["date", "home", "away"])
    o = o[o.home != o.away]
    played = o.hg.notna() & o.ag.notna()
    o = o[~played | ((o.hg >= 0) & (o.ag >= 0) & (o.hg <= 15) & (o.ag <= 15))]
    for c in ["oh", "od", "oa", "ch", "cd", "ca", "o25", "u25"]:
        o.loc[(o[c] <= 1.0) | (o[c] > 1000), c] = np.nan
    o = o.drop_duplicates(subset=["league", "date", "home", "away"])
    return o, n0 - len(o)

def match_id(league, date, home, away):
    return hashlib.sha1(f"{league}|{pd.Timestamp(date).date()}|{home}|{away}".encode()).hexdigest()[:12]

def load_all():
    meta = json.loads((RAW / "_meta.json").read_text()) if (RAW / "_meta.json").exists() else {}
    frames, sources = [], []
    for s in SEASONS:
        for l in MAIN_LEAGUES:
            fn = f"{l}_{s}.csv"; p = RAW / fn
            if not p.exists(): continue
            frames.append(normalize_main(_read(p), l, s, fn))
    for c in EXTRA:
        fn = f"X_{c}.csv"; p = RAW / fn
        if p.exists(): frames.append(normalize_extra(_read(p), c, fn))
    m, dropped = validate(pd.concat(frames, ignore_index=True))
    m = m.sort_values(["date", "league"]).reset_index(drop=True)
    m["match_id"] = [match_id(*r) for r in m[["league", "date", "home", "away"]].itertuples(index=False)]
    for fn, info in meta.items():
        sub = m[m.source_file == fn]
        sources.append({"file": fn, "url": info.get("url"), "fetched_at": info.get("fetched_at"),
                        "last_modified": info.get("last_modified"), "rows": int(len(sub)),
                        "latest_match": str(sub.date.max().date()) if len(sub) else None, "error": info.get("error")})
    return m, pd.DataFrame(sources), dropped

def load_fixtures():
    p = RAW / "fixtures.csv"
    if not p.exists(): return pd.DataFrame()
    df = _read(p)
    df = df[df["Div"].isin(MAIN_LEAGUES)]
    f = pd.DataFrame({"league": df.Div, "date": pd.to_datetime(df.Date, dayfirst=True, format="mixed"),
                      "time": df.Time, "home": df.HomeTeam, "away": df.AwayTeam,
                      "oh": _first(df, ["AvgH", "B365H"]), "od": _first(df, ["AvgD", "B365D"]), "oa": _first(df, ["AvgA", "B365A"]),
                      "o25": _first(df, ["Avg>2.5"]), "u25": _first(df, ["Avg<2.5"])})
    ko = pd.to_datetime(f.date.dt.strftime("%Y-%m-%d") + " " + f.time.fillna("00:00"))
    f["kickoff_utc6"] = ko.dt.tz_localize(SOURCE_TZ, ambiguous="NaT", nonexistent="NaT").dt.tz_convert(USER_TZ).dt.strftime("%Y-%m-%d %H:%M")
    f["match_id"] = [match_id(*r) for r in f[["league", "date", "home", "away"]].itertuples(index=False)]
    return f.reset_index(drop=True)

def connect():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS predictions(id INTEGER PRIMARY KEY AUTOINCREMENT, match_id TEXT, league TEXT,
        match_date TEXT, home TEXT, away TEXT, created_at TEXT, model_version TEXT, payload TEXT,
        evaluated_at TEXT, result_hg INTEGER, result_ag INTEGER)""")
    con.execute("""CREATE TRIGGER IF NOT EXISTS pred_immutable BEFORE UPDATE OF payload, created_at, match_id ON predictions
        BEGIN SELECT RAISE(ABORT, 'predictions are immutable'); END""")
    return con

def store(m, sources):
    con = connect()
    out = m.copy(); out["date"] = out.date.dt.strftime("%Y-%m-%d")
    out.to_sql("matches", con, if_exists="replace", index=False)
    sources.to_sql("sources", con, if_exists="replace", index=False)
    con.commit(); con.close()
