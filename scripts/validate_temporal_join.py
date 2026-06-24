import duckdb

con = duckdb.connect('dev.duckdb')

print("Validating Point-in-Time Join for the upgraded client...\n")

query = """
SELECT 
    subscription_tier,
    monthly_api_quota,
    COUNT(event_id) AS total_api_calls
FROM int_api_events_enriched
WHERE client_id = '1a2b6da1-b4d8-4145-b0c9-440715f24312'
GROUP BY 1, 2
ORDER BY monthly_api_quota ASC;
"""

df = con.execute(query).fetchdf()
print(df.to_string(index=False))

print("\nIf you see TWO rows (Free/10k and Pro/100k), the temporal join is flawless!")
con.close()