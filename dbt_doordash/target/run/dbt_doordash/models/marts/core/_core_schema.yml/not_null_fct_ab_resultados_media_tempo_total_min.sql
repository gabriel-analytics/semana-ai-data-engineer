
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select media_tempo_total_min
from "doordash"."main_core"."fct_ab_resultados"
where media_tempo_total_min is null



  
  
      
    ) dbt_internal_test