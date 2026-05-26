
WITH flights AS (
    SELECT * FROM {{ ref('stg_flights') }}
),

routes AS (
    SELECT
        route_id,
        origin,
        destination,
        is_strategic
    FROM {{ ref('stg_routes') }}
)

SELECT
    f.flight_id,
    f.route_id,
    f.flight_date,
    f.flight_year,
    f.flight_month_num,
    f.scheduled_departure,
    f.scheduled_arrival,
    f.actual_departure,
    f.actual_arrival,
    f.aircraft_type,
    f.seat_capacity,
    f.pax_boarded,
    f.load_factor,
    f.delay_minutes,
    f.total_revenue_usd,
    f.op_cost_usd,
    f.fuel_cost_usd,
    f.gross_margin_usd,
    f.flight_status,
    f.is_delayed,
    f.is_cancelled,
    f.delay_category,
    f.route_type,
    f.distance_km,
    r.origin,
    r.destination,
    r.is_strategic,

    CURRENT_TIMESTAMP                        AS updated_at

FROM flights f
LEFT JOIN routes r ON f.route_id = r.route_id