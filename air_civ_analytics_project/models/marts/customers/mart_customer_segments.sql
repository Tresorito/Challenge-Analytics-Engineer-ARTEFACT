WITH customer_metrics AS (
    SELECT * FROM {{ ref('int_customer_metrics') }}
)

SELECT
    customer_id,
    segment,
    loyalty_tier,
    loyalty_member,
    preferred_cabin,
    age_group,
    country,
    ROUND(ltv_usd, 2)                    AS ltv_usd,
    ROUND(total_fare_revenue, 2)         AS total_fare_revenue_usd,
    ROUND(total_ancillary_revenue, 2)    AS total_ancillary_revenue_usd,
    ROUND(avg_fare_paid, 2)              AS avg_fare_paid_usd,
    ROUND(ancillary_attach_rate, 4)      AS ancillary_attach_rate,
    total_bookings,
    total_flights,
    business_flights,
    last_booking_date,
    first_booking_date,
    days_since_last_booking,
    bookings_recent,
    bookings_older,
    total_miles_earned,
    total_miles_redeemed,
    open_tickets,
    ROUND(avg_rating, 2)                 AS avg_rating,
    ROUND(avg_review_sentiment, 4)       AS avg_review_sentiment,
    churn_signal_flight_drop,
    churn_signal_open_tickets,
    churn_signal_low_rating,
    churn_score,
    CURRENT_TIMESTAMP                    AS updated_at

FROM customer_metrics