
WITH bookings AS (
    SELECT * FROM {{ ref('stg_bookings') }}
),

flights AS (
    SELECT
        flight_id,
        route_id,
        flight_date,
        flight_year,
        flight_month_num,
        aircraft_type,
        route_type,
        is_cancelled
    FROM {{ ref('stg_flights') }}
)

SELECT
    b.booking_id,
    b.customer_id,
    b.flight_id,
    f.route_id,
    b.fare_family                            AS fare_family_id,
    b.booking_date,
    f.flight_date,
    f.flight_year,
    f.flight_month_num,
    b.fare_paid_usd,
    b.ancillary_revenue_usd,
    b.fare_paid_usd
        + b.ancillary_revenue_usd            AS total_revenue_usd,
    b.cabin,
    b.channel,
    b.fare_class,
    b.fare_family,
    b.bags_count,
    b.seat_selected,
    b.booking_status,
    b.is_cancelled,
    f.route_type,
    f.aircraft_type,

    CURRENT_TIMESTAMP                        AS updated_at

FROM bookings b
LEFT JOIN flights f ON b.flight_id = f.flight_id