import duckdb
import pandas as pd
import random


con = duckdb.connect('dev.duckdb') 

print("Fetching distinct client IDs from raw data...")

client_ids = con.execute("SELECT DISTINCT client_id FROM raw_api_events").fetchdf()['client_id'].tolist()

print("Generating client subscription tiers and quotas...")


tiers = [
    {'tier': 'Free', 'monthly_quota': 10000, 'overage_rate_per_1k': 2.00},
    {'tier': 'Pro', 'monthly_quota': 100000, 'overage_rate_per_1k': 1.50},
    {'tier': 'Enterprise', 'monthly_quota': 1000000, 'overage_rate_per_1k': 0.75}
]

data = []
for cid in client_ids:

    chosen_tier = random.choice(tiers)
    data.append({
        'client_id': cid,
        'subscription_tier': chosen_tier['tier'],
        'monthly_api_quota': chosen_tier['monthly_quota'],
        'overage_rate_per_1k_calls': chosen_tier['overage_rate_per_1k'],
        'updated_at': '2023-10-01 00:00:00' 
    })


df = pd.DataFrame(data)
df.to_csv('seeds/clients.csv', index=False)

print("Success! Saved 'seeds/clients.csv' with 50 clients.")
con.close()