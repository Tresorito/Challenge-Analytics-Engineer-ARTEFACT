-- Agrèger les KPIs financiers et opérationnels par route

WITH flights AS (
    SELECT * FROM {{ ref('stg_flights') }}
),

routes AS (
    SELECT * FROM {{ ref('stg_routes') }}
),

reviews AS (
    SELECT * FROM {{ ref('stg_reviews') }}
),

tickets AS (
    SELECT * FROM {{ ref('stg_tickets') }}
),

route_ops AS (
    SELECT
        route_id,

        COUNT(*)                                AS total_flights,
        SUM(CASE WHEN NOT is_cancelled
                 THEN 1 ELSE 0 END)            AS operated_flights,
        SUM(CASE WHEN NOT is_cancelled
                 THEN pax_boarded ELSE 0 END)  AS total_pax,

        SUM(CASE WHEN NOT is_cancelled
                 THEN total_revenue_usd
                 ELSE 0 END)                   AS total_revenue,
        SUM(CASE WHEN NOT is_cancelled
                 THEN op_cost_usd
                 ELSE 0 END)                   AS total_op_cost,

        AVG(CASE WHEN NOT is_cancelled
                 THEN load_factor END)         AS avg_load_factor,
        AVG(CASE WHEN is_delayed
                 THEN delay_minutes END)       AS avg_delay_min,

        SUM(CASE WHEN is_delayed
                 THEN 1 ELSE 0 END) * 1.0
          / NULLIF(COUNT(*), 0)                AS delay_rate,

        SUM(CASE WHEN is_cancelled
                 THEN 1 ELSE 0 END) * 1.0
          / NULLIF(COUNT(*), 0)                AS cancellation_rate,

        SUM(total_revenue_usd) * 1.0
          / NULLIF(SUM(pax_boarded), 0)        AS yield_per_pax

    FROM flights
    GROUP BY route_id
),
 
--Le NPS (Net Promoter Score) est une mesure de la satisfaction client basée sur la question : "Quelle est la probabilité que vous recommandiez notre service à un ami ou collègue ?". Les répondants sont classés en trois catégories : promoteurs (score 9-10), passifs (score 7-8) et détracteurs (score 0-6). Le NPS est calculé en soustrayant le pourcentage de détracteurs du pourcentage de promoteurs. Un NPS positif indique une base de clients satisfaite, tandis qu'un NPS négatif suggère des problèmes de satisfaction.
route_sentiment AS (
    SELECT
        f.route_id,
        AVG(r.sentiment_score)                 AS avg_sentiment,
        AVG(r.rating)                          AS avg_rating,
        COUNT(r.review_id)                     AS review_count,
        SUM(CASE WHEN r.nps_category = 'promoter'
                 THEN 1 ELSE 0 END)            AS promoters,
        SUM(CASE WHEN r.nps_category = 'detractor'
                 THEN 1 ELSE 0 END)            AS detractors
    FROM reviews r
    JOIN flights f ON r.flight_id = f.flight_id
    GROUP BY f.route_id
),

route_tickets AS (
    SELECT
        f.route_id,
        COUNT(t.ticket_id)                     AS ticket_count,
        COUNT(CASE WHEN t.category = 'delay'
                   THEN 1 END)                 AS delay_tickets,
        COUNT(CASE WHEN t.category = 'baggage'
                   THEN 1 END)                 AS baggage_tickets,
        COUNT(CASE WHEN t.category = 'service'
                   THEN 1 END)                 AS service_tickets
    FROM tickets t
    JOIN flights f ON t.flight_id = f.flight_id
    GROUP BY f.route_id
)


SELECT
    ro.route_id,
    r.origin,
    r.destination,
    r.route_type,
    r.distance_km,
    r.is_strategic,
    ro.total_flights,
    ro.operated_flights,
    ro.total_pax,
    ROUND(ro.total_revenue, 2)                 AS total_revenue_usd,
    ROUND(ro.total_op_cost, 2)                 AS total_op_cost_usd,
    ROUND(ro.total_revenue
        - ro.total_op_cost, 2)                 AS gross_margin_usd,
    ROUND(ro.avg_load_factor, 4)               AS avg_load_factor,
    ROUND(ro.yield_per_pax, 2)                 AS yield_per_pax_usd,
    ROUND(ro.delay_rate, 4)                    AS delay_rate,
    ROUND(ro.cancellation_rate, 4)             AS cancellation_rate,
    ROUND(ro.avg_delay_min, 1)                 AS avg_delay_minutes,
    ROUND(rs.avg_sentiment, 4)                 AS avg_sentiment,
    ROUND(rs.avg_rating, 2)                    AS avg_rating,
    COALESCE(rs.review_count, 0)               AS review_count,

    -- NPS proxy
    CASE
        WHEN COALESCE(rs.promoters, 0)
           + COALESCE(rs.detractors, 0) > 0
        THEN ROUND(
            (rs.promoters - rs.detractors) * 100.0
          / (rs.promoters + rs.detractors), 1)
        ELSE NULL
    END                                        AS nps_proxy,

    COALESCE(rt.ticket_count, 0)               AS ticket_count,
    COALESCE(rt.delay_tickets, 0)              AS delay_tickets,
    COALESCE(rt.baggage_tickets, 0)            AS baggage_tickets,
    COALESCE(rt.service_tickets, 0)            AS service_tickets,

    -- Marge par vol opéré
    ROUND(
        (ro.total_revenue - ro.total_op_cost)
      / NULLIF(ro.operated_flights, 0), 2)     AS margin_per_flight_usd

FROM route_ops ro
JOIN routes r
    ON ro.route_id = r.route_id
LEFT JOIN route_sentiment rs
    ON ro.route_id = rs.route_id
LEFT JOIN route_tickets rt
    ON ro.route_id = rt.route_id