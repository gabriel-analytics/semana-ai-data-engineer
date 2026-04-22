
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select delivery_duration_minutes
from "doordash"."main_staging"."stg_pedidos"
where delivery_duration_minutes is null



  
  
      
    ) dbt_internal_test