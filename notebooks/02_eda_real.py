"""EDA sobre el dataset REAL (data/playnova_real.db).

Genera las 3 figuras en docs/img/ e imprime resumen + tabla por título.
Todo lo que afirma docs/04_analisis.md sale de aquí.
"""
import os, sqlite3
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.style.use("dark_background")

DB = "data/playnova_real.db"
IMG = "docs/img"
NAMES = {570: "Dota 2", 440: "TF2", 230410: "Warframe", 238960: "PoE",
         1172470: "Apex", 1097150: "Fall Guys"}


def load():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM reviews WHERE churn IS NOT NULL", conn)
    conn.close()
    df["title"] = df["appid"].map(NAMES)
    return df


def fig_retention_titulo(df, path):
    t = df.groupby("title").agg(churn=("churn", "mean"), high_value=("high_value", "mean")).loc[
        ["Dota 2", "Apex", "TF2", "Warframe", "PoE", "Fall Guys"]]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(t))
    ax.bar(x - 0.2, t["churn"] * 100, 0.4, label="Churn (inactivos hoy)", color="#ef4444")
    ax.bar(x + 0.2, t["high_value"] * 100, 0.4, label="High-value (proxy)", color="#22d3ee")
    ax.set_xticks(x, t.index, color="#a0a0c0")
    ax.set_ylabel("% de reseñistas", color="#a0a0c0")
    ax.set_title("Estado del jugador por título (muestra de reseñistas, sep-2026)", color="#22d3ee", fontsize=13)
    leg = ax.legend()
    leg.get_frame().set_facecolor("#1e1b3a")
    ax.tick_params(colors="#a0a0c0")
    plt.tight_layout(); plt.savefig(path, bbox_inches="tight"); plt.close()
    print("Guardado:", path)


def fig_churn_engagement(df, path):
    df = df.copy()
    df["q"] = pd.qcut(df["hours_at_review"], 4, labels=["Q1\n(pocas h.)", "Q2", "Q3", "Q4\n(muchas h.)"])
    t = df.groupby("q", observed=True)["churn"].mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    t.plot(kind="bar", ax=ax, color="#8b5cf6", edgecolor="#22d3ee")
    ax.set_title("Churn según horas jugadas en el momento de la reseña", color="#8b5cf6", fontsize=13)
    ax.set_xlabel("Cuartil de engagement temprano", color="#a0a0c0")
    ax.set_ylabel("Tasa de churn", color="#a0a0c0")
    ax.tick_params(colors="#a0a0c0")
    plt.tight_layout(); plt.savefig(path, bbox_inches="tight"); plt.close()
    print("Guardado:", path)


def fig_voto_vs_churn(df, path):
    t = df.groupby("voted_up")["churn"].mean()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(["No recomienda", "Recomienda"], t.values * 100, color=["#f59e0b", "#22d3ee"])
    ax.set_title("Satisfacción ≠ retención", color="#22d3ee", fontsize=13)
    ax.set_ylabel("Tasa de churn", color="#a0a0c0")
    for i, v in enumerate(t.values * 100):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha="center", color="#e8e8f0")
    ax.tick_params(colors="#a0a0c0")
    plt.tight_layout(); plt.savefig(path, bbox_inches="tight"); plt.close()
    print("Guardado:", path)


def main():
    os.makedirs(IMG, exist_ok=True)
    df = load()
    print(f"Filas: {len(df)} · churn={df['churn'].mean():.1%} · high_value={df['high_value'].mean():.1%} "
          f"· recomienda={df['voted_up'].mean():.1%}")
    print("\nPor título:")
    print(df.groupby("title").agg(n=("churn", "size"), churn=("churn", "mean"),
          high_value=("high_value", "mean"),
          med_horas_reseña=("hours_at_review", "median")).round({"churn": 3, "high_value": 3, "med_horas_reseña": 1}).to_string())
    fig_retention_titulo(df, f"{IMG}/retention_titulo.png")
    fig_churn_engagement(df, f"{IMG}/churn_engagement.png")
    fig_voto_vs_churn(df, f"{IMG}/voto_vs_churn.png")
    print("\nEDA real completo.")


if __name__ == "__main__":
    main()
