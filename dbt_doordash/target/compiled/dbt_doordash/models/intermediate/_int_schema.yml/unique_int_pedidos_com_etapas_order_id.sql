
    
    

select
    order_id as unique_field,
    count(*) as n_records

from "doordash"."main_intermediate"."int_pedidos_com_etapas"
where order_id is not null
group by order_id
having count(*) > 1


