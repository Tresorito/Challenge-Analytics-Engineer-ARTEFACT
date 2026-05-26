-- Calculer les métriques clés par client : LTV, churn, ancillaires
WITH bookings AS (
    SELECT * FROM {{ ref('stg_bookings') }}
),

reviews AS (
    SELECT * FROM {{ ref('stg_reviews') }}
),

tickets AS (
    SELECT * FROM {{ ref('stg_tickets') }}
),

loyalty AS (
    SELECT * FROM {{ ref('stg_loyalty') }}
),

customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

customer_revenue AS (
    SELECT
        customer_id,
        COUNT(DISTINCT booking_id)          AS total_bookings,
        COUNT(DISTINCT flight_id)           AS total_flights,
        SUM(fare_paid_usd)                  AS total_fare_revenue,
        AVG(fare_paid_usd)                  AS avg_fare_paid,
        SUM(ancillary_revenue_usd)          AS total_ancillary_revenue,
        MAX(booking_date)                   AS last_booking_date,
        MIN(booking_date)                   AS first_booking_date,

        COUNT(CASE
            WHEN booking_date >= CURRENT_DATE - INTERVAL '9 months'
            THEN 1 END)                     AS bookings_recent,

        COUNT(CASE
            WHEN booking_date < CURRENT_DATE - INTERVAL '9 months'
            THEN 1 END)                     AS bookings_older,

        COUNT(CASE
            WHEN cabin = 'business'
            THEN 1 END)                     AS business_flights

    FROM bookings
    GROUP BY customer_id
),

customer_loyalty AS (
    SELECT
        customer_id,
        SUM(miles_earned)                   AS total_miles_earned,
        SUM(miles_redeemed)                 AS total_miles_redeemed,
        COUNT(loyalty_id)                   AS loyalty_transactions
    FROM loyalty
    GROUP BY customer_id
),

customer_tickets AS (
    SELECT
        customer_id,
        COUNT(CASE
            WHEN is_open = TRUE
            THEN 1 END)                     AS open_tickets
    FROM tickets
    GROUP BY customer_id
),

customer_satisfaction AS (
    SELECT
        customer_id,
        AVG(rating)                         AS avg_rating,
        AVG(sentiment_score)                AS avg_review_sentiment
    FROM reviews
    GROUP BY customer_id
),

final AS (
    SELECT
        c.customer_id,
        c.segment,
        c.loyalty_tier,
        c.loyalty_member,
        c.preferred_cabin,
        c.age_group,
        c.country,

        COALESCE(cr.total_fare_revenue, 0)
          + COALESCE(cr.total_ancillary_revenue, 0)   AS ltv_usd,

        COALESCE(cr.total_fare_revenue, 0)            AS total_fare_revenue,
        COALESCE(cr.total_ancillary_revenue, 0)       AS total_ancillary_revenue,
        COALESCE(cr.total_bookings, 0)                AS total_bookings,
        COALESCE(cr.total_flights, 0)                 AS total_flights,
        COALESCE(cr.avg_fare_paid, 0)                 AS avg_fare_paid,
        COALESCE(cr.business_flights, 0)              AS business_flights,
        cr.last_booking_date,
        cr.first_booking_date,
        COALESCE(cr.bookings_recent, 0)               AS bookings_recent,
        COALESCE(cr.bookings_older, 0)                AS bookings_older,

        COALESCE(cl.total_miles_earned, 0)            AS total_miles_earned,
        COALESCE(cl.total_miles_redeemed, 0)          AS total_miles_redeemed,

        COALESCE(ct.open_tickets, 0)                  AS open_tickets,
        COALESCE(cs.avg_rating, 0)                    AS avg_rating,
        COALESCE(cs.avg_review_sentiment, 0)          AS avg_review_sentiment,

        CASE
            WHEN COALESCE(cr.total_fare_revenue, 0) > 0
            THEN ROUND(
                COALESCE(cr.total_ancillary_revenue, 0)
                / cr.total_fare_revenue, 4)
            ELSE 0
        END                                           AS ancillary_attach_rate,

        CASE
            WHEN COALESCE(cr.bookings_older, 0) > 0
             AND COALESCE(cr.bookings_recent, 0)
                 < cr.bookings_older * 0.60
            THEN 1 ELSE 0
        END                                           AS churn_signal_flight_drop,

        CASE
            WHEN COALESCE(ct.open_tickets, 0) >= 2
            THEN 1 ELSE 0
        END                                           AS churn_signal_open_tickets,

        CASE
            WHEN COALESCE(cs.avg_rating, 5) <= 2
            THEN 1 ELSE 0
        END                                           AS churn_signal_low_rating

    FROM customers c
    LEFT JOIN customer_revenue      cr ON c.customer_id = cr.customer_id
    LEFT JOIN customer_loyalty      cl ON c.customer_id = cl.customer_id
    LEFT JOIN customer_tickets      ct ON c.customer_id = ct.customer_id
    LEFT JOIN customer_satisfaction cs ON c.customer_id = cs.customer_id
)

SELECT
    *,
    churn_signal_flight_drop
      + churn_signal_open_tickets
      + churn_signal_low_rating               AS churn_score,
    DATEDIFF('day', last_booking_date, CURRENT_DATE) AS days_since_last_booking

FROM final