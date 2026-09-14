"""NO PAIN NO GAME — Datos REALES desde Riot Games API (EUW).

Que trae y que NO trae la API publica:
  SI trae: Riot ID -> PUUID, nivel summoner, rank (league-v4),
           ultimas partidas (match-v5): win, KDA, duracion, fecha.
  NO trae: tienda/compras, reportes toxicidad, logins/sesiones,
           tutorial, amigos, campanas/marketing, churn_60d.
           Por eso el modelo churn sigue entrenado con la muestra
           sintetica coherente (data/riot_gaming.db) y esto es la
           PRUEBA REAL: mismos features calculados con partidas de verdad.

Uso:
  1. Consigue development key (24h) en https://developer.riotgames.com/
     (login con cuenta Riot -> te dan RGAPI-xxxxxxxx)
  2. En PowerShell:
       $env:RIOT_API_KEY="RGAPI-xxxxxxxx"
       python src/fetch_riot.py --players "Rekkles#EUW,Ibai#EUW1" --matches 20
     Por defecto usa 5 Riot IDs EUW conocidos si no pasas --players.
  3. Genera: data/riot_real_matches.csv + data/riot_real_players.csv
     (features reales: winrate, KDA, duracion media, partidas 30d aprox.)

Rate limits development key: ~20 req/s y 100 req/2min. El script
lleva pausa de 1.2s entre partidas para no baneos.
"""
from __future__ import annotations
import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_MATCHES = ROOT / "data" / "riot_real_matches.csv"
OUT_PLAYERS = ROOT / "data" / "riot_real_players.csv"

EUROPE = "https://europe.api.riotgames.com"
EUW1 = "https://euw1.api.riotgames.com"

DEFAULT_PLAYERS = [
    "Rekkles#EUW",
    "Caps#EUW1",
    "Jankos#EUW",
    "Mikyx#EUW",
    "Hans Sama#EUW1",
]


def headers(key: str) -> dict:
    return {"X-Riot-Token": key}


def get_account(game: str, tag: str, key: str) -> dict:
    url = f"{EUROPE}/riot/account/v1/accounts/by-riot-id/{game}/{tag}"
    r = requests.get(url, headers=headers(key), timeout=15)
    if r.status_code == 401:
        sys.exit("ERROR 401: API key invalida o caducada. Regenera en developer.riotgames.com y exporta $env:RIOT_API_KEY")
    if r.status_code == 404:
        raise ValueError(f"Riot ID no encontrado: {game}#{tag}")
    r.raise_for_status()
    return r.json()  # puuid, gameName, tagLine


def get_summoner(puuid: str, key: str) -> dict:
    url = f"{EUW1}/lol/summoner/v4/summoners/by-puuid/{puuid}"
    r = requests.get(url, headers=headers(key), timeout=15)
    if r.status_code == 404:
        return {}
    r.raise_for_status()
    return r.json()


def get_rank(puuid: str, key: str) -> str:
    # Por PUUID (recomendado). Fallback a summonerId si hace falta.
    url = f"{EUW1}/lol/league/v4/entries/by-puuid/{puuid}"
    r = requests.get(url, headers=headers(key), timeout=15)
    if r.status_code != 200:
        return "Unranked"
    entries = r.json()
    for e in entries:
        if e.get("queueType") == "RANKED_SOLO_5x5":
            return e.get("tier", "Unranked").capitalize()
    return entries[0].get("tier", "Unranked").capitalize() if entries else "Unranked"


def get_match_ids(puuid: str, key: str, count: int) -> list:
    url = f"{EUROPE}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    r = requests.get(url, headers=headers(key), params={"count": count, "queue": 420}, timeout=15)
    # queue 420 = ranked solo. Si no tiene, reintentar sin filtro.
    if r.status_code == 200 and r.json():
        return r.json()
    r = requests.get(url, headers=headers(key), params={"count": count}, timeout=15)
    r.raise_for_status()
    return r.json()


def get_match(match_id: str, key: str) -> dict:
    url = f"{EUROPE}/lol/match/v5/matches/{match_id}"
    r = requests.get(url, headers=headers(key), timeout=15)
    if r.status_code == 429:
        time.sleep(5)
        r = requests.get(url, headers=headers(key), timeout=15)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--players", default=",".join(DEFAULT_PLAYERS),
                    help="Riot IDs separados por coma, formato GameName#TAG")
    ap.add_argument("--matches", type=int, default=20, help="Partidas por jugador (max ~30 con dev key)")
    args = ap.parse_args()

    key = os.getenv("RIOT_API_KEY", "").strip()
    if not key or not key.startswith("RGAPI-"):
        sys.exit("Falta $env:RIOT_API_KEY. Haz: $env:RIOT_API_KEY=\"RGAPI-xxxx\" (key de https://developer.riotgames.com/)")

    riot_ids = [p.strip() for p in args.players.split(",") if "#" in p]
    if not riot_ids:
        sys.exit("Formato: GameName#TAG, ej: Rekkles#EUW")

    all_matches, rows = [], []
    for rid in riot_ids:
        game, tag = rid.split("#", 1)
        print(f"> {rid} ...")
        try:
            acc = get_account(game.strip(), tag.strip(), key)
        except ValueError as e:
            print(f"  ! {e} (s historic? prueba otro Riot ID)")
            continue
        puuid = acc["puuid"]
        summ = get_summoner(puuid, key)
        rank = get_rank(puuid, key)
        try:
            ids = get_match_ids(puuid, key, args.matches)
        except Exception as e:
            print(f"  ! no matches: {e}")
            continue
        print(f"  puuid ok, nivel {summ.get('summonerLevel','?')}, rank {rank}, {len(ids)} partidas")
        wins, kdas, durs = 0, [], []
        for mid in ids:
            try:
                m = get_match(mid, key)
            except Exception as e:
                print(f"    ! {mid}: {e}")
                continue
            info = m["info"]
            dur = info.get("gameDuration", 0) / 60
            dt = datetime.fromtimestamp(info.get("gameCreation", 0) / 1000, tz=timezone.utc).date().isoformat()
            for p in info["participants"]:
                if p.get("puuid") == puuid:
                    win = int(p.get("win", False))
                    k, d, a = p.get("kills", 0), max(1, p.get("deaths", 1)), p.get("assists", 0)
                    kda = (k + a) / d
                    wins += win
                    kdas.append(kda)
                    durs.append(dur)
                    all_matches.append({
                        "riot_id": rid, "match_id": mid, "date": dt,
                        "win": win, "kills": k, "deaths": d, "assists": a,
                        "kda": round(kda, 2), "duration_min": round(dur, 1),
                        "champion": p.get("championName", ""),
                    })
                    break
            time.sleep(1.2)  # respetar rate limit dev key
        n = len(kdas) or 1
        rows.append({
            "riot_id": rid,
            "puuid": puuid,
            "summoner_level": summ.get("summonerLevel", ""),
            "rank_tier": rank,
            "matches_muestra": len(kdas),
            "winrate_muestra": round(wins / n, 3),
            "kda_medio": round(sum(kdas) / n, 2),
            "duracion_media_min": round(sum(durs) / n, 1) if durs else "",
        })

    if not rows:
        sys.exit("No se pudo descargar nada. Revisa key y Riot IDs.")

    pd.DataFrame(all_matches).to_csv(OUT_MATCHES, index=False)
    pd.DataFrame(rows).to_csv(OUT_PLAYERS, index=False)
    print(f"\nOK: {len(rows)} jugadores, {len(all_matches)} partidas")
    print(f"  -> {OUT_MATCHES}")
    print(f"  -> {OUT_PLAYERS}")
    print("\nNOTA: esto NO sustituye data/riot_gaming.db (la API no da tienda, toxicidad, logins ni churn).")
    print("Usalo en la presentacion como 'prueba real': compara winrate/KDA reales vs sintetica.")


if __name__ == "__main__":
    main()
