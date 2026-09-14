import sqlite3, pandas as pd, matplotlib.pyplot as plt, matplotlib
matplotlib.use('Agg')
import numpy as np

plt.style.use('dark_background')

DB_PATH = "data/playnova_games.db"
IMG_DIR = "docs/img"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    features = pd.read_sql("SELECT pf.*, p.acquisition_channel FROM player_features pf JOIN players p ON pf.player_id = p.player_id", conn)
    leads = pd.read_sql("SELECT l.*, c.channel FROM leads l JOIN campaigns c ON l.campaign_id = c.campaign_id", conn)
    conn.close()
    return features, leads

def plot_churn_toxicity(features, path):
    fig, ax = plt.subplots(figsize=(8,5))
    report_bins = pd.cut(features['ads_watched_7d'], bins=5)
    churn_by_reports = features.groupby(report_bins)['churn_d7'].mean()
    churn_by_reports.plot(kind='bar', ax=ax, color='#22d3ee', edgecolor='#8b5cf6')
    ax.set_title('Churn D7 vs Ads Watched (7d)', color='#22d3ee', fontsize=14)
    ax.set_xlabel('Ads Watched Bins', color='#a0a0c0')
    ax.set_ylabel('Churn Rate', color='#a0a0c0')
    ax.tick_params(colors='#a0a0c0')
    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {path}")

def plot_channel_conversion(leads, path):
    fig, ax = plt.subplots(figsize=(8,5))
    conv_by_channel = leads.groupby('channel')['converted_30d'].mean()
    conv_by_channel.plot(kind='bar', ax=ax, color='#8b5cf6', edgecolor='#22d3ee')
    ax.set_title('Conversion Rate 30d by UA Channel', color='#8b5cf6', fontsize=14)
    ax.set_xlabel('Channel', color='#a0a0c0')
    ax.set_ylabel('Conversion Rate', color='#a0a0c0')
    ax.tick_params(colors='#a0a0c0')
    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {path}")

def plot_winrate_churn(features, path):
    fig, ax = plt.subplots(figsize=(8,5))
    features['winrate_proxy'] = (features['coins_spent_7d'] / (features['session_count_7d'] + 1)).clip(0, 1)
    churn_0 = features[features['churn_d7']==0]['winrate_proxy']
    churn_1 = features[features['churn_d7']==1]['winrate_proxy']
    ax.hist([churn_0, churn_1], bins=20, label=['Retained', 'Churned'], color=['#22d3ee','#ef4444'], alpha=0.7)
    ax.set_title('Winrate Proxy Distribution by Churn', color='#22d3ee', fontsize=14)
    ax.set_xlabel('Winrate Proxy', color='#a0a0c0')
    ax.set_ylabel('Count', color='#a0a0c0')
    ax.legend(color='#a0a0c0')
    ax.tick_params(colors='#a0a0c0')
    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {path}")

def main():
    import os; os.makedirs(IMG_DIR, exist_ok=True)
    features, leads = load_data()
    print(f"Features: {len(features)} rows, Leads: {len(leads)} rows")
    plot_churn_toxicity(features, f"{IMG_DIR}/churn_toxicidad.png")
    plot_channel_conversion(leads, f"{IMG_DIR}/conv_canal.png")
    plot_winrate_churn(features, f"{IMG_DIR}/winrate_churn.png")
    print("\nEDA completo.")
    print(f"\nChurn rate global: {features['churn_d7'].mean():.1%}")
    print(f"Conversion rate global: {leads['converted_30d'].mean():.1%}")
    print(f"Tutorial completion: {features['tutorial_completed'].mean():.1%}")
    print(f"Retention by channel:")
    for ch in features['acquisition_channel'].unique():
        subset = features[features['acquisition_channel']==ch]
        print(f"  {ch}: {subset['churn_d7'].mean():.1%} churn")

if __name__ == "__main__": main()
