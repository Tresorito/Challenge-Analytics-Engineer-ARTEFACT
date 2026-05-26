WITH source AS (
    SELECT * FROM {{ source('raw', 'support_tickets') }}
),
cleaned AS (
    SELECT
        ticket_id,
        customer_id,
        flight_id,
        category,
        ticket_text,
        CAST(sentiment_score AS DOUBLE)     AS sentiment_score,
        sentiment_label,
        severity,
        status,
        CAST(created_at AS DATE)            AS created_at,
        CAST(resolution_days AS INTEGER)    AS resolution_days,
        CASE
            WHEN status IN ('open', 'in_progress') THEN TRUE
            ELSE FALSE
        END AS is_open

    FROM source
    WHERE ticket_id IS NOT NULL
)
SELECT * FROM cleaned