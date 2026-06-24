-- models/staging/stg_api_events.sql

WITH source AS (
    SELECT * FROM raw_api_events
),

cleaned AS (
    SELECT
        -- Standardize UUIDs and Timestamps
        CAST(event_id AS VARCHAR) AS event_id,
        CAST(request_timestamp AS TIMESTAMP) AS request_timestamp,
        CAST(client_id AS VARCHAR) AS client_id,
        
        -- Data Cleaning: Normalize endpoints to lowercase so /V1/AUTH and /v1/auth are treated the same
        LOWER(CAST(endpoint AS VARCHAR)) AS endpoint,
        
        -- Standardize HTTP methods to uppercase
        UPPER(CAST(http_method AS VARCHAR)) AS http_method,
        
        -- Cast numerics and handle potential nulls
        CAST(status_code AS INTEGER) AS status_code,
        
        -- If response_time is null or weird, default to 0, otherwise cast to int
        COALESCE(CAST(response_time_ms AS INTEGER), 0) AS response_time_ms,
        
        -- Keep payload size as is, but ensure it's an integer
        CAST(payload_size_kb AS INTEGER) AS payload_size_kb
        
    FROM source
)

SELECT * FROM cleaned