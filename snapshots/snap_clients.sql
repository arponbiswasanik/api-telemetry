{% snapshot snap_clients %}

{{
    config(
      target_schema='snapshots',
      unique_key='client_id',
      strategy='timestamp',
      updated_at='updated_at'
    )
}}

SELECT * FROM {{ ref('clients') }}

{% endsnapshot %}