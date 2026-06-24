-- models/marts/fct_monthly_api_usage.sql

WITH monthly_aggregation AS (
    SELECT
        billing_month,
        client_id,
        subscription_tier,
        monthly_api_quota,
        overage_rate_per_1k_calls,
        -- Count the total API calls for this client in this month
        COUNT(event_id) AS total_api_calls,
        
        -- Calculate the P95 latency for this client in this month
        -- We use a percentile_cont function to find the 95th percentile response time
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_latency_ms
        
    FROM {{ ref('int_api_events_enriched') }}
    GROUP BY 1, 2, 3, 4, 5
),

billing_calculations AS (
    SELECT
        *,
        
        -- How many calls were made over the quota? (Cannot be negative)
        GREATEST(total_api_calls - monthly_api_quota, 0) AS calls_over_quota,
        
        -- Is this client over their limit this month?
        CASE 
            WHEN total_api_calls > monthly_api_quota THEN TRUE 
            ELSE FALSE 
        END AS is_over_quota
        
    FROM monthly_aggregation
)

SELECT
    *,
    
    -- Final Overage Cost = (Overage Calls / 1000) * Rate per 1k
    -- We use ROUND to keep it to 2 decimal places like real currency
    ROUND((calls_over_quota / 1000.0) * overage_rate_per_1k_calls, 2) AS overage_cost_usd

FROM billing_calculations