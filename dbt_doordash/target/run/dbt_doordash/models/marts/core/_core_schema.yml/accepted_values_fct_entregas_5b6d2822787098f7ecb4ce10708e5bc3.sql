
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

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



  
  
      
    ) dbt_internal_test