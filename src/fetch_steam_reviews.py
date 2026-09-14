"""Descarga reseñas públicas de Steam (sin API key) para títulos F2P.

Endpoint público: https://store.steampowered.com/appreviews/{appid}?json=1
100 reseñas por petición, paginación por cursor. Reanuda si existe el .jsonl.

Uso:
    python src/fetch_steam_reviews.py [--per-title 3000] [--sleep 1.0]

Salida: data/real/steam_reviews.jsonl (una reseña por línea + appid/appname).
"""
import argparse, json, os, sys, time
import requests

TITLES = [
    (570, "Dota 2"),
    (440, "Team Fortress 2"),
    (230410, "Warframe"),
    (238960, "Path of Exile"),
    (1172470, "Apex Legends"),
    (1097150, "Fall Guys"),
]

OUT = "data/real/steam_reviews.jsonl"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "ChurnGuard-bootcamp/1.0 (research; contact: piloto@churnguard.gg)"})

def fetch_title(appid, appname, per_title, sleep_s, seen):
    got, cursor = 0, "*"
    while got < per_title:
        params = {"json": 1, "language": "all", "purchase_type": "all",
                  "num_per_page": 100, "filter": "recent", "cursor": cursor}
        try:
            r = SESSION.get(f"https://store.steampowered.com/appreviews/{appid}",
                            params=params, timeout=30)
        except requests.RequestException as e:
            print(f"  [{appname}] red {e}, reintento en 10s"); time.sleep(10); continue
        if r.status_code == 429:
            print(f"  [{appname}] 429, espero 30s"); time.sleep(30); continue
        if r.status_code != 200:
            print(f"  [{appname}] HTTP {r.status_code}, fin"); break
        try:
            d = r.json()
        except ValueError:
            print(f"  [{appname}] JSON inválido, fin"); break
        if not d.get("success"):
            print(f"  [{appname}] success=0, fin"); break
        new = 0
        with open(OUT, "a", encoding="utf-8") as f:
            for rev in d.get("reviews", []):
                rid = str(rev.get("recommendationid"))
                if rid in seen:
                    continue
                seen.add(rid)
                rev["_appid"] = appid
                rev["_appname"] = appname
                f.write(json.dumps(rev, ensure_ascii=False) + "\n")
                new += 1
        got += new
        cursor = d.get("cursor", "")
        total = d.get("query_summary", {}).get("total_reviews", "?")
        print(f"  [{appname}] +{new} (acum objetivo {got}/{per_title}, total tienda {total})")
        if not d.get("reviews") or not cursor:
            break
        time.sleep(sleep_s)
    return got

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-title", type=int, default=3000)
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()
    os.makedirs("data/real", exist_ok=True)
    seen = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            for line in f:
                try:
                    seen.add(str(json.loads(line).get("recommendationid")))
                except ValueError:
                    pass
        print(f"Reanudo: {len(seen)} reseñas ya descargadas en {OUT}")
    total = 0
    for appid, appname in TITLES:
        print(f"Descargando {appname} ({appid})…")
        total += fetch_title(appid, appname, args.per_title, args.sleep, seen)
    print(f"\nHecho: +{total} reseñas nuevas. Total en {OUT}: {len(seen)}")

if __name__ == "__main__":
    main()
