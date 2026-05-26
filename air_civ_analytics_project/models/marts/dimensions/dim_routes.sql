WITH source AS (
    SELECT * FROM {{ ref('stg_routes') }}
)

SELECT
    route_id,
    origin,
    destination,
    route_type,
    distance_km,
    block_time_min,
    is_strategic,
    origin || ' → ' || destination           AS route_label,
    CASE
        WHEN distance_km < 500  THEN 'short'
        WHEN distance_km < 2000 THEN 'medium'
        ELSE 'long'
    END                                      AS distance_category,

    CURRENT_TIMESTAMP                        AS updated_at
FROM source