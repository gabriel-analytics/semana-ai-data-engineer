
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select status
from "doordash"."main_staging"."stg_pedidos"
where status is null



  
  
      
    ) dbt_internal_test