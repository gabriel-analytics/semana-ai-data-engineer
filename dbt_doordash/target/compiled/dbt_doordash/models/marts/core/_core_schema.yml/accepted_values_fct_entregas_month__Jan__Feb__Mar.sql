
    
    

with all_values as (

    select
        month as value_field,
        count(*) as n_records

    from "doordash"."main_core"."fct_entregas"
    group by month

)

select *
from all_values
where value_field not in (
    'Jan','Feb','Mar'
)


