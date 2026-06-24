-- models/intermediate/int_api_events_enriched.sql

WITH events AS (
    SELECT * FROM {{ ref('stg_api_events') }}
),

client_history AS (
    -- DBT automatically adds dbt_valid_from and dbt_valid_to columns to snapshots!
    SELECT * FROM {{ ref('snap_clients') }}
),

enriched AS (
    SELECT
        e.event_id,
        e.request_timestamp,
        CAST(strftime(e.request_timestamp, '%Y-%m') AS VARCHAR) AS billing_month,
        e.client_id,
        e.endpoint,
        e.http_method,
        e.status_code,
        e.response_time_ms,
        e.payload_size_kb,
        
        -- Join business context using POINT-IN-TIME logic
        c.subscription_tier,
        c.monthly_api_quota,
        c.overage_rate_per_1k_calls
        
    FROM events e
    LEFT JOIN client_history c 
        ON e.client_id = c.client_id
        -- Match the event to the snapshot record that was valid at that exact time
        AND e.request_timestamp >= c.dbt_valid_from
        AND (e.request_timestamp < c.dbt_valid_to OR c.dbt_valid_to IS NULL)
)

SELECT * FROM enriched