WITH source AS (
    SELECT * FROM {{ source('raw', 'customers') }}
),
cleaned AS (
    SELECT
        customer_id,
        first_name,
        last_name,
        gender,
        CAST(birth_date AS DATE)                AS birth_date,
        country,
        city,
        segment,
        loyalty_tier,
        CAST(loyalty_member AS BOOLEAN)         AS loyalty_member,
        CAST(signup_date AS DATE)               AS signup_date,
        preferred_channel,
        preferred_cabin,
        CAST(age AS INTEGER)                    AS age,
        CASE
            WHEN age < 25 THEN '18-24'
            WHEN age < 35 THEN '25-34'
            WHEN age < 45 THEN '35-44'
            WHEN age < 55 THEN '45-54'
            ELSE '55+'
        END AS age_group

    FROM source
    WHERE customer_id IS NOT NULL
)
SELECT * FROM cleaned