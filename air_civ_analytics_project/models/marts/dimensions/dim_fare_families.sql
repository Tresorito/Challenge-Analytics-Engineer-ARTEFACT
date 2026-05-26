WITH source AS (
    SELECT * FROM {{ source('raw', 'bookings') }}
)

SELECT DISTINCT
    fare_family                              AS fare_family_id,
    fare_class,
    fare_family,
    CASE
        WHEN fare_class = 'Business' THEN 'business'
        ELSE 'economy'
    END                                      AS cabin,
    CASE
        WHEN fare_family = 'Flex'     THEN 'full'
        WHEN fare_family = 'Standard' THEN 'change_only'
        ELSE 'none'
    END                                      AS flexibility,
    CASE
        WHEN fare_family = 'Basic'    THEN 0.75
        WHEN fare_family = 'Standard' THEN 1.00
        WHEN fare_family = 'Flex'     THEN 1.35
        WHEN fare_family = 'Business' THEN 3.20
        ELSE 1.00
    END                                      AS price_multiplier,

    CURRENT_TIMESTAMP                        AS updated_at
FROM source
WHERE fare_family IS NOT NULL