# API Telemetry 

## Overview

A high-volume analytics pipeline that processes 500,000 raw B2B API gateway logs to calculate monthly usage, P95 latency, and tiered overage billing. Built to simulate the backend infrastructure of a Developer Platform (e.g., Twilio, Stripe, or AWS).

This project goes beyond simple aggregations. It implements **Slowly Changing Dimensions (SCD Type 2)** to handle mid-month subscription upgrades, ensuring that financial billing is temporally accurate — events are always evaluated against the business rules that were active at the exact millisecond the API call was made.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data Generation | Python (Pandas, NumPy) — Simulates high-traffic, messy API telemetry |
| Data Warehouse | DuckDB — An in-process, columnar OLAP database for blazing-fast analytics |
| Transformation & Modeling | DBT (Data Build Tool) — Version-controlled SQL transformations, automated data testing, and SCD2 snapshots |
| Visualization | Power BI (via ODBC) — Connects directly to the analytical warehouse for executive reporting |

---

## Key Engineering Features

- **Point-in-Time Temporal Joins:** Utilizes DBT snapshots to join event streams against historical business rules, preventing billing corruption when clients upgrade tiers mid-month.
- **Data Quality Enforcement:** Implements `dbt test` to ensure primary keys are unique and critical billing fields are never null.
- **Statistical Aggregations:** Calculates exact P95 latency percentiles using SQL window functions to monitor SLA compliance.
- **Tiered Billing Logic:** Translates complex business rules (quota limits, variable overage rates per 1k calls) into scalable SQL math.

---

## Project Structure

```text
api-telemetry/
├── models/
│   ├── staging/
│   │   ├── stg_api_events.sql          # Cleans raw logs (normalizes endpoints, handles nulls)
│   │   └── schema.yml                  # Defines data quality tests (unique, not_null)
│   ├── intermediate/
│   │   └── int_api_events_enriched.sql # Point-in-time join between events and client history
│   └── marts/
│       └── fct_monthly_api_usage.sql   # Final fact table: total calls, P95 latency, overage costs
├── scripts/
│   ├── generate_logs.py                # Generates 500k rows of messy raw API logs
│   ├── generate_clients.py             # Generates client seed data with tiers and quotas
│   ├── simulate_upgrade.py             # Simulates a CRM update (mid-month tier upgrade)
│   └── validate_billing.py             # Python script to audit billing calculations
├── snapshots/
│   └── snap_clients.sql                # DBT SCD2 snapshot configuration for client subscriptions
├── seeds/
│   └── clients.csv                     # Static business data loaded via dbt seed
├── .gitignore
├── dbt_project.yml
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Setup Environment

Clone the repository and install the required Python packages.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Generate Raw Data

Run the Python scripts to simulate the API gateway logs and client CRM data. Then, trigger a mid-month upgrade to test the SCD2 logic.

```bash
python scripts/generate_logs.py
python scripts/generate_clients.py
dbt seed
python scripts/simulate_upgrade.py
```

### 3. Build the Data Pipeline

Run the DBT models to clean, enrich, and calculate billing. Then, execute tests to verify data integrity.

```bash
dbt snapshot  # Captures the SCD2 history
dbt run       # Builds staging, intermediate, and marts
dbt test      # Validates data quality
```

### 4. Visualization (Power BI)

To visualize the billing metrics and API volume:

1. Connect **Power BI Desktop** to the `dev.duckdb` file using the DuckDB connector (or via ODBC).
2. Load the `fct_monthly_api_usage` table.
3. Build visuals showing **Total Calls by Tier**, **P95 Latency trends**, and a filtered table of **Clients with Overage Costs** (> $0).

---

## Business Impact

This pipeline allows finance and operations teams to:

- **Accurately invoice** B2B clients for API overages without manual Excel calculations.
- **Identify clients** who are consistently hitting their quotas (upsell opportunities).
- **Monitor P95 latency** by endpoint to enforce Service Level Agreements (SLAs).