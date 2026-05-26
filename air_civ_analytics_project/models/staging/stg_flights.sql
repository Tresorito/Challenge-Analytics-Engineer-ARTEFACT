WITH source AS (

    SELECT * FROM {{ source('raw', 'flights') }}

),

cleaned AS (

    SELECT
        flight_id,
        flight_number,
        route_id,
        flight_date,
        scheduled_departure,
        scheduled_arrival,
        actual_departure,
        actual_arrival,
        aircraft_type,
        CAST(seat_capacity AS INTEGER)          AS seat_capacity,
        flight_status,
        CAST(delay_minutes AS INTEGER)          AS delay_minutes,
        is_delayed,
        is_cancelled,
        route_type,
        CAST(distance_km AS INTEGER)            AS distance_km,
        CAST(pax_boarded AS INTEGER)            AS pax_boarded,
        CAST(load_factor AS DOUBLE)             AS load_factor,
        CAST(total_revenue_usd AS DOUBLE)       AS total_revenue_usd,
        CAST(op_cost_usd AS DOUBLE)             AS op_cost_usd,
        CAST(fuel_cost_usd AS DOUBLE)           AS fuel_cost_usd,
        CASE
            WHEN delay_minutes >= 180 THEN 'major'
            WHEN delay_minutes >= 60  THEN 'significant'
            WHEN delay_minutes >= 15  THEN 'minor'
            ELSE 'on_time'
        END                                     AS delay_category,

        CAST(total_revenue_usd AS DOUBLE)
            - CAST(op_cost_usd AS DOUBLE)       AS gross_margin_usd,

        EXTRACT('month' FROM flight_date)       AS flight_month_num,
        EXTRACT('year'  FROM flight_date)       AS flight_year

    FROM source
    WHERE flight_id IS NOT NULL

)

SELECT * FROM cleaned