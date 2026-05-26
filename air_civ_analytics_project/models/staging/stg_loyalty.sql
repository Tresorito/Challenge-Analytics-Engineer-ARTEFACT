WITH source AS (
    SELECT * FROM {{ source('raw', 'loyalty_activity') }}
),
cleaned AS (
    SELECT
        loyalty_id,
        customer_id,
        booking_id,
        CAST(transaction_date AS DATE)      AS transaction_date,
        CAST(miles_earned AS INTEGER)       AS miles_earned,
        CAST(miles_redeemed AS INTEGER)     AS miles_redeemed,
        activity_type,
        CAST(miles_earned AS INTEGER)
            - CAST(miles_redeemed AS INTEGER) AS miles_net

    FROM source
    WHERE loyalty_id IS NOT NULL
)
SELECT * FROM cleaned