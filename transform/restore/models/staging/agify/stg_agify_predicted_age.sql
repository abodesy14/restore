with src as (
    select *
    from predicted_age
)

select 
    distinct name as first_name,
    age as predicted_age,
    count as rows_examined
from src