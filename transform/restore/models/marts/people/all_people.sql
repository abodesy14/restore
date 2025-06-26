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
    if(password ~ '[A-Z]', 1, 0) as password_has_upper,
    if(password ~ '[a-z]', 1, 0) as password_has_lower,
    if(password ~ '[0-9]', 1, 0) as password_has_numeric,
    -- insert special?
    len(password) as password_length,
    if(password_has_upper + password_has_lower + password_has_numeric = 3, 1, 0) as good_password,
    age - predicted_age as age_delta
from predicted_ages