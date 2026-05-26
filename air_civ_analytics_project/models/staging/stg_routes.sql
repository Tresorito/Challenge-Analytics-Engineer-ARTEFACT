WITH source AS (
    SELECT * FROM {{ source('raw', 'routes') }}
),
cleaned AS (
    SELECT
        route_id,
        origin_airport_code     AS origin,
        destination_airport_code AS destination,
        route_type,
        CAST(distance_km AS INTEGER)        AS distance_km,
        CAST(block_time_min AS INTEGER)     AS block_time_min,
        CASE
            WHEN route_type IN ('International', 'longhaul') THEN TRUE
            ELSE FALSE
        END AS is_strategic

    FROM source
    WHERE route_id IS NOT NULL
)
SELECT * FROM cleaned