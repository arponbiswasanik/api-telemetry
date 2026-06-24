import duckdb

# Connect to the database
con = duckdb.connect('dev.duckdb')

print("Top 10 Clients by Overage Cost:\n")

# Query the fact table we just built
query = """
SELECT 
    billing_month,
    client_id,
    subscription_tier,
    monthly_api_quota,
    total_api_calls,
    calls_over_quota,
    overage_cost_usd
FROM fct_monthly_api_usage
WHERE overage_cost_usd > 0
ORDER BY overage_cost_usd DESC
LIMIT 10;
"""

# Execute and fetch results into a pandas dataframe for pretty printing
df = con.execute(query).fetchdf()
print(df.to_string(index=False))

con.close()