WITH route_metrics AS (
    SELECT * FROM {{ ref('int_route_metrics') }}
)

SELECT
    route_id,
    origin,
    destination,
    route_type,
    distance_km,
    is_strategic,
    total_flights,
    operated_flights,
    total_pax,
    total_revenue_usd,
    total_op_cost_usd,
    gross_margin_usd,
    yield_per_pax_usd,
    margin_per_flight_usd,
    ROUND(avg_load_factor * 100, 1)      AS load_factor_pct,
    ROUND(delay_rate * 100, 1)           AS delay_rate_pct,
    ROUND(cancellation_rate * 100, 1)    AS cancellation_rate_pct,
    avg_delay_minutes,
    avg_sentiment,
    avg_rating,
    nps_proxy,
    review_count,
    ticket_count,
    delay_tickets,
    baggage_tickets,
    service_tickets,
    CURRENT_TIMESTAMP                    AS updated_at

FROM route_metrics