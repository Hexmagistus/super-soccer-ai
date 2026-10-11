"""Daily pipeline: refresh data -> validate/store -> (optional) backtest -> predict -> store immutable
timestamped predictions -> evaluate finished predictions.  Usage: python pipeline.py [--force] [--backtest]"""
import sys, json, datetime as dt
import pandas as pd
from ssa import ingest
from ssa.models import add_features
from ssa.predict import predict_fixtures
from ssa import backtest

def main(argv):
    ingest.download(force="--force" in argv)
    m, sources, dropped = ingest.load_all(); ingest.store(m, sources)
    print(f"loaded {len(m)} matches ({dropped} rows dropped by validation)")
    m = add_features(m)
    if "--backtest" in argv or not (backtest.REPORTS / "backtest.json").exists():
        backtest.run(m)
    fx = ingest.load_fixtures()
    preds = predict_fixtures(m, fx)
    con = ingest.connect()
    for p in preds:
        con.execute("INSERT INTO predictions(match_id,league,match_date,home,away,created_at,model_version,payload) VALUES(?,?,?,?,?,?,?,?)",
                    (p["match_id"], p["league"], p["date"], p["home"], p["away"], p["created_at"], p["model_version"], json.dumps(p)))
    # evaluate finished predictions (results now present in matches)
    done = 0
    for pid, mid in con.execute("SELECT id, match_id FROM predictions WHERE evaluated_at IS NULL").fetchall():
        r = con.execute("SELECT hg, ag FROM matches WHERE match_id=? AND hg IS NOT NULL", (mid,)).fetchone()
        if r:
            con.execute("UPDATE predictions SET evaluated_at=?, result_hg=?, result_ag=? WHERE id=?",
                        (dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), int(r[0]), int(r[1]), pid)); done += 1
    con.commit(); con.close()
    print(f"stored {len(preds)} predictions; evaluated {done} finished ones")

if __name__ == "__main__":
    main(sys.argv[1:])
