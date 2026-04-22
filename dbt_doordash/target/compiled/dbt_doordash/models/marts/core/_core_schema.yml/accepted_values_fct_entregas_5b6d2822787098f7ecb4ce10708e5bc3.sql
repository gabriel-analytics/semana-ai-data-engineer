
    
    

with all_values as (

    select
        classificacao_entrega as value_field,
        count(*) as n_records

    from "doordash"."main_core"."fct_entregas"
    group by classificacao_entrega

)

select *
from all_values
where value_field not in (
    'rapida','normal','lenta'
)


