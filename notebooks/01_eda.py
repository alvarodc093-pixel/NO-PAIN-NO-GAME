"""EDA No Pain, No Game — ejecutable como script o notebook.
Uso: python notebooks/01_eda.py  (genera docs/img/*.png)
"""
import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "riot_gaming.db"
IMG = ROOT / "docs" / "img"
IMG.mkdir(exist_ok=True)

con = sqlite3.connect(DB)
df = pd.read_sql("SELECT * FROM player_features", con)
leads = pd.read_sql("SELECT * FROM new_leads", con)
camps = pd.read_sql("SELECT * FROM campaigns", con)
con.close()
cmap = dict(zip(camps.campaign_id, camps.channel))
leads["channel"] = leads.campaign_id.map(cmap)

print(f"players={len(df)} churn={df.churn_60d.mean():.3f} leads={len(leads)} conv={leads.converted_30d.mean():.3f}")
print("\n-- churn por toxicidad --\n", df.assign(b=pd.cut(df.toxicity_received_30d, [-1,0,1,99], labels=["0","1","2+"])).groupby("b", observed=True).churn_60d.mean())
print("\n-- churn por social --\n", df.assign(b=pd.cut(df.solo_rate_30d, [-0.01,0.33,0.66,1.01], labels=["grupo","mixto","solo"])).groupby("b", observed=True).churn_60d.mean())
print("\n-- conv por canal --\n", leads.groupby("channel").converted_30d.mean().sort_values(ascending=False))
print("\n-- conv por tutorial --\n", leads.groupby("tutorial_completed").converted_30d.mean())

fig, ax = plt.subplots(figsize=(6, 4))
(df.assign(b=pd.cut(df.toxicity_received_30d, [-1,0,1,99], labels=["0","1","2+"]))
   .groupby("b", observed=True).churn_60d.mean().plot(kind="bar", ax=ax, color="#ff4b4b"))
ax.set_title("Churn por reportes de toxicidad (30d)")
ax.set_ylabel("Tasa churn"); fig.tight_layout(); fig.savefig(IMG / "churn_toxicidad.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
(leads.groupby("channel").converted_30d.mean().sort_values(ascending=False)
   .plot(kind="bar", ax=ax, color="#21c55d"))
ax.set_title("Conversión 30d por canal de adquisición")
ax.set_ylabel("Tasa conversión"); fig.tight_layout(); fig.savefig(IMG / "conv_canal.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(df[df.churn_60d==0].winrate_30d, bins=20, alpha=0.6, label="se queda")
ax.hist(df[df.churn_60d==1].winrate_30d, bins=20, alpha=0.6, label="abandona")
ax.set_title("Winrate 30d: se queda vs abandona"); ax.legend()
fig.tight_layout(); fig.savefig(IMG / "winrate_churn.png"); plt.close(fig)
print("Figuras en docs/img/")
