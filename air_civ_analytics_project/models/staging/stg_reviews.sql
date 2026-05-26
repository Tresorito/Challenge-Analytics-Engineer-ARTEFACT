WITH source AS (
    SELECT * FROM {{ source('raw', 'customer_reviews') }}
),
cleaned AS (
    SELECT
        review_id,
        booking_id,
        customer_id,
        flight_id,
        CAST(review_date AS DATE)           AS review_date,
        CAST(rating AS INTEGER)             AS rating,
        review_text,
        CAST(sentiment_score AS DOUBLE)     AS sentiment_score,
        sentiment_label,
        cabin,
        CASE
            WHEN rating >= 4 THEN 'promoter'
            WHEN rating <= 2 THEN 'detractor'
            ELSE 'passive'
        END AS nps_category

    FROM source
    WHERE review_id IS NOT NULL
)
SELECT * FROM cleaned