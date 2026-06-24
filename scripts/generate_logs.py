import duckdb
import pandas as pd
import numpy as np
import uuid
import random
from datetime import datetime, timedelta

# Connect to the DuckDB database
con = duckdb.connect('dev.duckdb')

print("Generating 500,000 raw API event logs using Pandas...")

num_rows = 500000
clients = [str(uuid.uuid4()) for _ in range(50)]
endpoints = ['/v1/auth', '/v1/users', '/v1/billing', '/v1/messages', '/v1/analytics']
methods = ['GET', 'POST', 'PUT', 'DELETE']

# Create base dataframe
df = pd.DataFrame({
    'event_id': [str(uuid.uuid4()) for _ in range(num_rows)],
    'client_id': [random.choice(clients) for _ in range(num_rows)],
    'endpoint': [random.choice(endpoints) for _ in range(num_rows)],
    'http_method': [random.choice(methods) for _ in range(num_rows)],
})

# Simulate time progression over 30 days
start_time = datetime(2023, 10, 1, 0, 0, 0)
df['request_timestamp'] = [start_time + timedelta(seconds=random.randint(0, 2592000)) for _ in range(num_rows)]

# Simulate status codes
status_roll = np.random.rand(num_rows)
df['status_code'] = 200
df.loc[status_roll >= 0.85, 'status_code'] = random.choice([400, 401, 403, 404])
df.loc[status_roll >= 0.95, 'status_code'] = random.choice([500, 502, 503])

# Simulate response time (P95/P99 logic)
response_times = np.random.randint(20, 400, num_rows)
slow_tail = np.random.randint(1000, 5000, num_rows)
slow_mask = np.random.rand(num_rows) > 0.95
df['response_time_ms'] = np.where(slow_mask, slow_tail, response_times)

# Simulate payload size with occasional NULLs
df['payload_size_kb'] = np.random.randint(1, 512, num_rows)
df.loc[df.sample(frac=0.01).index, 'payload_size_kb'] = None

# Make endpoint messy: sometimes uppercase
messy_mask = np.random.rand(num_rows) > 0.8
df.loc[messy_mask, 'endpoint'] = df.loc[messy_mask, 'endpoint'].str.upper()

# CRITICAL FIX: Explicitly order columns to match the database schema exactly
df = df[['event_id', 'request_timestamp', 'client_id', 'endpoint', 'http_method', 'status_code', 'response_time_ms', 'payload_size_kb']]

# Create the raw table in DuckDB
con.execute("""
    CREATE OR REPLACE TABLE raw_api_events (
        event_id VARCHAR,
        request_timestamp TIMESTAMP,
        client_id VARCHAR,
        endpoint VARCHAR,
        http_method VARCHAR,
        status_code INTEGER,
        response_time_ms INTEGER,
        payload_size_kb INTEGER
    );
""")

# Register the pandas dataframe and insert it
con.register('df_view', df)
con.execute("INSERT INTO raw_api_events SELECT * FROM df_view")

# Verify
count = con.execute("SELECT COUNT(*) FROM raw_api_events").fetchone()[0]
print(f"Success! Loaded {count} rows into 'raw_api_events'.")
con.close()