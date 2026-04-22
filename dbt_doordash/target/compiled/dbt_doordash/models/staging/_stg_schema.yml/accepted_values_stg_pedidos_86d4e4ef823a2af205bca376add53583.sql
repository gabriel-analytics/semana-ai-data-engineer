
    
    

with all_values as (

    select
        status as value_field,
        count(*) as n_records

    from "doordash"."main_staging"."stg_pedidos"
    group by status

)

select *
from all_values
where value_field not in (
    'delivered','cancelled','in_progress'
)


