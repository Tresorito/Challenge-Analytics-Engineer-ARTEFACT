
WITH source AS (
    SELECT * FROM {{ ref('stg_customers') }}
)

SELECT
    customer_id,
    first_name,
    last_name,
    gender,
    age,
    age_group,
    country,
    city,
    segment,
    loyalty_member,
    loyalty_tier,
    COALESCE(loyalty_tier, 'non_member')     AS loyalty_tier_clean,
    preferred_cabin,
    preferred_channel,
    birth_date,
    signup_date,
    CURRENT_TIMESTAMP                        AS updated_at
FROM source