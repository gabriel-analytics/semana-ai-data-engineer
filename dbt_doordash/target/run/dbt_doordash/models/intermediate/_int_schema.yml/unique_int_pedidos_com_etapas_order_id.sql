
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    order_id as unique_field,
    count(*) as n_records

from "doordash"."main_intermediate"."int_pedidos_com_etapas"
where order_id is not null
group by order_id
having count(*) > 1



  
  
      
    ) dbt_internal_test