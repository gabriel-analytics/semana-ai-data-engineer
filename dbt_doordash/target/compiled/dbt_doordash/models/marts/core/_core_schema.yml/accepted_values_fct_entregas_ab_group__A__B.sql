
    
    

with all_values as (

    select
        ab_group as value_field,
        count(*) as n_records

    from "doordash"."main_core"."fct_entregas"
    group by ab_group

)

select *
from all_values
where value_field not in (
    'A','B'
)


