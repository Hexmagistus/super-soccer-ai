"""South Africa Premier Soccer League (Betway Premiership) provider adapter.

Source of results: English Wikipedia season articles "<YYYY>–<YY> South African Premiership", section
"Results" (the {{#invoke:sports results}} home/away matrix), fetched through the MediaWiki API
(https://en.wikipedia.org/w/api.php, allowed by robots.txt; content CC BY-SA 4.0, attribution: Wikipedia
contributors). The revision id + revision timestamp + fetch time are recorded for every season.

Limitations (never filled in / never fabricated):
  * The matrix has NO match dates or kickoff times -> date is NULL; models use season-level ordering only.
  * No odds, no shots, no xG.
  * Results struck through on Wikipedia (expunged, e.g. Royal AM 2024-25) and "Canc." cells are excluded.
  * No free, key-less, terms-compatible source of upcoming PSL fixtures was found -> fixtures unavailable
    (see adapters.api_football_psl_fixtures for an optional API_FOOTBALL_KEY stub).

Cross-check source: openfootball/world africa/south-africa/2024-25_za1.txt (public domain, dated results).
football-data.co.uk new/RSA.csv was re-checked on 2026-10-11: it 302/301-redirects to new/USA.csv (MLS,
identical SHA-1), so it is NOT used."""
import re, json, hashlib, datetime as dt
import pandas as pd, requests
from .config import RAW

CODE = "PSL"
NAME = "South Africa Premiership (PSL / Betway Premiership)"
SEASONS = ["2021–22", "2022–23", "2023–24", "2024–25", "2025–26", "2026–27"]
API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "SuperSoccerAI/0.1 (https://github.com/Hexmagistus/super-soccer-ai; research, low volume)"}
OPENFOOTBALL = "https://raw.githubusercontent.com/openfootball/world/master/africa/south-africa/2024-25_za1.txt"
CANON = {"Lamontville Golden Arrows": "Golden Arrows", "Moroka Swallows": "Swallows"}
NOW = lambda: dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def page_title(season): return f"{season} South African Premiership"
def season_key(season): return season.replace("–", "-")

def canon(name):
    n = re.sub(r"\s+(F\.?C\.?)$", "", name.strip()); return CANON.get(n, n)

def download(force=False):
    RAW.mkdir(parents=True, exist_ok=True); meta_p = RAW / "_psl_meta.json"
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
    for s in SEASONS:
        fn = f"PSL_wikipedia_{season_key(s)}.wikitext"; p = RAW / fn
        complete = meta.get(fn, {}).get("complete")
        if p.exists() and not force and complete: continue  # finished seasons are frozen once fetched
        try:
            r = requests.get(API, params={"action": "query", "prop": "revisions", "titles": page_title(s), "rvprop": "ids|timestamp|content",
                                          "rvslots": "main", "format": "json", "formatversion": 2, "redirects": 1}, headers=UA, timeout=30)
            r.raise_for_status(); pg = r.json()["query"]["pages"][0]; rev = pg["revisions"][0]
            txt = rev["slots"]["main"]["content"]; p.write_text(txt)
            upd = re.search(r"\|\s*update\s*=\s*([^\n|]*)", _block(txt) or "")
            meta[fn] = {"url": f"https://en.wikipedia.org/w/index.php?title={pg['title'].replace(' ', '_')}&oldid={rev['revid']}",
                        "api": API, "title": pg["title"], "revid": rev["revid"], "revision_timestamp": rev["timestamp"],
                        "fetched_at": NOW(), "sha1": hashlib.sha1(txt.encode()).hexdigest(), "license": "CC BY-SA 4.0 (Wikipedia contributors)",
                        "update_field": upd.group(1).strip() if upd else None,
                        "complete": bool(upd and upd.group(1).strip() == "complete") or s < SEASONS[-1]}
        except Exception as e:
            meta.setdefault(fn, {})["error"] = f"{type(e).__name__}: {e}"; print("PSL download failed", s, e)
    meta_p.write_text(json.dumps(meta, indent=1)); return meta

def _block(txt):
    i = txt.find("{{#invoke:sports results")
    if i < 0: return None
    depth, j = 0, i
    while j < len(txt):
        if txt.startswith("{{", j): depth += 1; j += 2; continue
        if txt.startswith("}}", j):
            depth -= 1; j += 2
            if depth == 0: return txt[i:j]
            continue
        j += 1
    return None

def parse(txt, season):
    """Return (rows, excluded). rows: home, away, hg, ag. Excluded: struck-through/cancelled/blank cells."""
    blk = _block(txt)
    if not blk: raise ValueError("no sports results matrix")
    blk = re.sub(r"<!--.*?-->", "", blk, flags=re.S)
    blk = re.sub(r"\{\{small\|([^{}|]*)\}\}", r"<small>\1</small>", blk)
    blk = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", blk)      # [[link|text]] -> text
    blk = re.sub(r"\{\{(?:efn|refn|sfn|cref)[^{}]*\}\}|<ref[^>]*/>|<ref.*?</ref>", "", blk, flags=re.S)
    params = {}
    for part in blk[2:-2].split("|")[1:]:
        if "=" in part: k, v = part.split("=", 1); params[k.strip()] = v.strip()
    names = {k[5:]: canon(re.sub(r"<[^>]+>", "", v)) for k, v in params.items() if k.startswith("name_")}
    rows, excl = [], []
    for k, v in params.items():
        mm = re.fullmatch(r"match_([A-Za-z0-9]+)_([A-Za-z0-9]+)", k)
        if not mm: continue
        h, a = names.get(mm.group(1)), names.get(mm.group(2))
        if h is None or a is None: raise ValueError(f"unknown team code in {k}")
        if "<s>" in v or "<del>" in v or "Canc" in v or "w/o" in v.lower():
            excl.append({"home": h, "away": a, "cell": v}); continue
        sc = re.fullmatch(r"(\d+)\s*[–\-−]\s*(\d+)", re.sub(r"<[^>]+>", "", v).strip())
        if not sc:
            if v.strip(): excl.append({"home": h, "away": a, "cell": v})
            continue
        rows.append({"league": CODE, "season": season_key(season), "home": h, "away": a, "hg": int(sc.group(1)), "ag": int(sc.group(2))})
    return rows, excl, sorted(set(names.values()))

def load(validate_strict=True):
    meta = json.loads((RAW / "_psl_meta.json").read_text()) if (RAW / "_psl_meta.json").exists() else {}
    frames, report = [], {}
    for s in SEASONS:
        fn = f"PSL_wikipedia_{season_key(s)}.wikitext"; p = RAW / fn
        if not p.exists(): continue
        rows, excl, teams = parse(p.read_text(), s); df = pd.DataFrame(rows)
        issues = []
        if len(teams) != 16: issues.append(f"{len(teams)} teams (expected 16)")
        if df.duplicated(["home", "away"]).any(): issues.append("duplicate home/away pair")
        if (df.home == df.away).any(): issues.append("team plays itself")
        if ((df.hg > 10) | (df.ag > 10)).any(): issues.append("implausible score > 10")
        complete = meta.get(fn, {}).get("complete")
        if complete and len(df) + len(excl) != 240: issues.append(f"{len(df)} played + {len(excl)} excluded != 240")
        if validate_strict and any("duplicate" in i or "itself" in i for i in issues): raise ValueError(f"PSL {s}: {issues}")
        df["source_file"] = fn; df["source_url"] = meta.get(fn, {}).get("url"); df["date"] = None
        df["match_id"] = [hashlib.sha1(f"{CODE}|{r.season}|{r.home}|{r.away}".encode()).hexdigest()[:12] for r in df.itertuples()]
        tc = table_check(p.read_text(), df)
        if tc and tc["teams_matching"] == tc["teams_checked"]: status = "verified"
        elif tc and all(o["table"][:3] == o["matrix"][:3] for o in tc["mismatches"]): status = "outcomes_verified_goals_inconsistent"
        else: status = "failed_consistency"
        df["data_status"] = status; frames.append(df)
        report[season_key(s)] = {"teams": teams, "n_teams": len(teams), "played": int(len(df)), "excluded": len(excl),
                                 "excluded_cells": excl[:40], "issues": issues, "complete": bool(complete), "table_check": tc, "data_status": status,
                                 "goals_per_match": round(float((df.hg + df.ag).mean()), 3) if len(df) else None,
                                 "home_win_rate": round(float((df.hg > df.ag).mean()), 3) if len(df) else None,
                                 **{k: meta.get(fn, {}).get(k) for k in ("url", "revid", "revision_timestamp", "fetched_at", "update_field")}}
    m = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return m, report

def table_check(txt, m_season):
    """Internal consistency: W/D/L/GF/GA computed from the results matrix vs the page's own league table."""
    i = txt.find("{{#invoke:Sports table")
    if i < 0: return None
    t = txt[i:i + 20000]; out = []
    agg = {}
    for r in m_season.itertuples():
        for team, gf, ga in ((r.home, r.hg, r.ag), (r.away, r.ag, r.hg)):
            a = agg.setdefault(team, [0, 0, 0, 0, 0]); a[0 if gf > ga else 1 if gf == ga else 2] += 1; a[3] += gf; a[4] += ga
    codes = dict(re.findall(r"\|\s*name_(\w+)\s*=\s*(?:\[\[(?:[^|\]]*\|)?)?([^\]\n|]*)", t))
    for c, n in codes.items():
        vals = [re.search(rf"\|\s*{k}_{c}\s*=\s*(\d+)", t) for k in ("win", "draw", "loss", "gf", "ga")]
        if all(vals) and canon(n) in agg:
            tab = [int(v.group(1)) for v in vals]; out.append({"team": canon(n), "table": tab, "matrix": agg[canon(n)], "match": tab == agg[canon(n)]})
    return {"teams_checked": len(out), "teams_matching": sum(o["match"] for o in out), "mismatches": [o for o in out if not o["match"]]}

def parse_openfootball(txt):
    """Parse openfootball 'Football.TXT' (2024-25 PSL) -> dated results."""
    out, date, year = [], None, None
    for line in txt.splitlines():
        d = re.match(r"\s+(?:\w{3})\s+(\w{3})\s+(\d{1,2})(?:\s+(\d{4}))?\s*$", line)
        if d:
            year = d.group(3) or year; date = pd.to_datetime(f"{d.group(2)} {d.group(1)} {year}"); continue
        mm = re.match(r"\s+(?:\d{1,2}:\d{2})?\s*(.+?)\s+v\s+(.+?)\s{2,}(\d+)-(\d+)", line)
        if mm and date is not None:
            out.append({"date": str(date.date()), "home": canon(mm.group(1)), "away": canon(mm.group(2)), "hg": int(mm.group(3)), "ag": int(mm.group(4))})
    return pd.DataFrame(out)

def cross_check(m):
    """Compare Wikipedia 2024-25 results with openfootball (independent second source)."""
    try:
        r = requests.get(OPENFOOTBALL, headers=UA, timeout=30); r.raise_for_status()
        (RAW / "PSL_openfootball_2024-25.txt").write_bytes(r.content); fetched = NOW()
    except Exception as e:
        p = RAW / "PSL_openfootball_2024-25.txt"
        if not p.exists(): return {"ok": False, "error": str(e)}
        r = None; fetched = None
    of = parse_openfootball((RAW / "PSL_openfootball_2024-25.txt").read_text())
    w = m[m.season == "2024-25"][["home", "away", "hg", "ag"]]
    j = of.merge(w, on=["home", "away"], how="left", suffixes=("_of", "_wp"))
    agree = j.dropna(subset=["hg_wp"]); dis = agree[(agree.hg_of != agree.hg_wp) | (agree.ag_of != agree.ag_wp)]
    return {"ok": True, "source": OPENFOOTBALL, "fetched_at": fetched, "openfootball_results": int(len(of)),
            "matched": int(len(agree)), "unmatched_in_wikipedia": j[j.hg_wp.isna()][["date", "home", "away"]].to_dict("records")[:20],
            "score_disagreements": dis[["date", "home", "away", "hg_of", "ag_of", "hg_wp", "ag_wp"]].to_dict("records"),
            "agreement_rate": round(1 - len(dis) / max(len(agree), 1), 4)}


USABLE = ("verified", "outcomes_verified_goals_inconsistent")

def backtest(m):
    """Season-ahead backtest (the source has no dates, so no in-season refits are possible): for each test season,
    fit Poisson and Dixon-Coles on ALL usable earlier seasons (season-level decay: weight 0.5 per season back),
    predict every match of the test season, and compare with base rates of the training seasons and 'always home'.
    Ensemble = fixed 50/50 Poisson/DC (no weight tuning, so no validation season is consumed)."""
    import numpy as np
    from .models import PoissonModel, DixonColes, outcome_probs
    from .backtest import metric_block, ci, y_of, logloss, calibration
    m = m[m.data_status.isin(USABLE)].copy()
    done = sorted(s for s in m.season.unique() if s != season_key(SEASONS[-1]))  # current season is partial
    ref = pd.Timestamp("2000-01-01"); rows = []
    for k, test in enumerate(done):
        prev = done[:k]
        if not prev: continue
        tr = m[m.season.isin(prev)].copy()
        tr["date"] = [ref - pd.Timedelta(days=365 * (len(prev) - prev.index(s))) for s in tr.season]  # weighting device only
        P = PoissonModel(xi=np.log(2) / 365).fit(tr, ref); D = DixonColes(xi=np.log(2) / 365).fit(tr, ref)
        base = tr.assign(r=np.sign(tr.hg - tr.ag)).r.value_counts(normalize=True).reindex([1, 0, -1]).fillna(0).values
        for r in m[m.season == test].itertuples():
            pp = outcome_probs(P.predict(r.home, r.away)[0]); pd_ = outcome_probs(D.predict(r.home, r.away)[0])
            rows.append({"season": test, "hg": r.hg, "ag": r.ag, "poisson": pp, "dc": pd_, "ens": (pp + pd_) / 2, "base": base,
                         "home_always": np.array([1.0, 0, 0]), "new_team": int(r.home not in P.idx) + int(r.away not in P.idx)})
    def summ(sub):
        res = {"n_matches": len(sub)}
        for key in ("poisson", "dc", "ens", "base"): res[key] = metric_block(sub, key)
        ha = [float(y_of(o) == 0) for o in sub]; res["home_always"] = {"n": len(sub), "accuracy": round(float(np.mean(ha)), 4), "accuracy_ci": ci(ha)}
        d = [logloss(o["ens"], y_of(o)) - logloss(o["base"], y_of(o)) for o in sub]
        res["ens_minus_base_logloss"] = {"mean": round(float(np.mean(d)), 4), "ci": ci(d)}
        res["calibration_bins"], res["ece"] = calibration(sub); return res
    out = summ(rows) if rows else {"n_matches": 0}
    out["by_season"] = {s: {k: v for k, v in summ([o for o in rows if o["season"] == s]).items() if k in ("n_matches", "ens", "base", "dc", "poisson")}
                        for s in sorted({o["season"] for o in rows})}
    out["method"] = backtest.__doc__.strip()
    out["missing"] = "No odds (no bookmaker benchmark, no value backtest), no shots, no dates (no Elo/form/logit models)."
    out["seasons_used"] = sorted(m.season.unique().tolist())
    return out
