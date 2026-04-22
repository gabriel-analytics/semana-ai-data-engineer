
    
    

with all_values as (

    select
        customer_city as value_field,
        count(*) as n_records

    from "doordash"."main_staging"."stg_pedidos"
    group by customer_city

)

select *
from all_values
where value_field not in (
    'São Paulo','Rio de Janeiro','Belo Horizonte','Curitiba','Porto Alegre','Brasília'
)


