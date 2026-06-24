import duckdb

# Connect to the database
con = duckdb.connect('dev.duckdb')

print("Simulating a client upgrading from Free to Pro on Oct 15th...")

# Let's find a Free client who actually went over their quota to make it interesting
client_to_upgrade = con.execute("""
    SELECT client_id FROM clients 
    WHERE subscription_tier = 'Free' 
    LIMIT 1
""").fetchone()[0]

# Run the update query to change their tier, quota, and timestamp
update_query = f"""
    UPDATE clients
    SET 
        subscription_tier = 'Pro',
        monthly_api_quota = 100000,
        updated_at = '2023-10-15 12:00:00'
    WHERE client_id = '{client_to_upgrade}'
"""

con.execute(update_query)

print(f"Success! Client {client_to_upgrade} is now Pro.")
print("Their history will be split on October 15th.")

con.close()