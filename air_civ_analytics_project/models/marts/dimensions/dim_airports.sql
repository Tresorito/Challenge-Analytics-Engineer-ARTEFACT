WITH source AS (
    SELECT * FROM {{ source('raw', 'airports') }}
)

SELECT
    airport_code                             AS airport_id,
    airport_name,
    city,
    country,
    timezone,
    CAST(latitude AS DOUBLE)                 AS latitude,
    CAST(longitude AS DOUBLE)                AS longitude,
    CASE
        WHEN airport_code = 'ABJ' THEN TRUE
        ELSE FALSE
    END                                      AS is_hub,
    CURRENT_TIMESTAMP                        AS updated_at
FROM source