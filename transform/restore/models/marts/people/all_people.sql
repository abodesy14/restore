with source as (
    select 
        *
    from {{ ref('stg_people') }}
),

predicted_ages as (
    select 
        s.*,
        pa.predicted_age
    from source s
    left join {{ ref('stg_agify_predicted_age')}} pa on pa.first_name = s.first_name
)

select 
    *,
    concat(first_name, ' ', last_name) as full_name,
    len(password) as password_length,
    if(regexp_matches(password, '[A-Z]'), 1, 0) AS password_has_upper,
    if(regexp_matches(password, '[a-z]'), 1, 0) AS password_has_lower,
    if(regexp_matches(password, '[0-9]'), 1, 0) AS password_has_numeric,
    if(password_length >= 8, 1, 0) as password_has_length,
    password_has_upper + password_has_lower + password_has_numeric + password_has_length as password_complexity_score,
    if(password_has_upper + password_has_lower + password_has_numeric + password_has_length >= 3, 1, 0) as good_password,
    age - predicted_age as age_delta,
    split_part(timezone_offset, ':', 1) as hour_tz_adjustment,
    split_part(timezone_offset, ':', 2) as minute_tz_adjustment
from predicted_ages