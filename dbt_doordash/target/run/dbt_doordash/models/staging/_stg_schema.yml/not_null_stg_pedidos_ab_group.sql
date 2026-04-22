
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select ab_group
from "doordash"."main_staging"."stg_pedidos"
where ab_group is null



  
  
      
    ) dbt_internal_test