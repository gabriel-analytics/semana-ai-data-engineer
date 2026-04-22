
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select duracao_preparo_min
from "doordash"."main_intermediate"."int_pedidos_com_etapas"
where duracao_preparo_min is null



  
  
      
    ) dbt_internal_test