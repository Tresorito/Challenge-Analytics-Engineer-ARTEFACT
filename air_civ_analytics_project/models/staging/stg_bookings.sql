WITH source AS (
    SELECT * FROM {{ source('raw', 'bookings') }}
),
cleaned AS (
    SELECT
        booking_id,
        flight_id,
        customer_id,
        CAST(booking_date AS DATE)              AS booking_date,
        booking_channel                         AS channel,
        fare_class,
        fare_family,
        CAST(ticket_price_usd AS DOUBLE)        AS fare_paid_usd,
        CAST(ancillary_revenue_usd AS DOUBLE)   AS ancillary_revenue_usd,
        CAST(bags_count AS INTEGER)             AS bags_count,
        CAST(seat_selection_flag AS BOOLEAN)    AS seat_selected,
        booking_status,
        CASE
            WHEN fare_class = 'Business' THEN 'business'
            ELSE 'economy'
        END AS cabin,
        CASE
            WHEN booking_status = 'Cancelled' THEN TRUE
            ELSE FALSE
        END AS is_cancelled

    FROM source
    WHERE booking_id IS NOT NULL
)
SELECT * FROM cleaned