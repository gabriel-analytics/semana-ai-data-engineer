
    
    

select
    ab_group as unique_field,
    count(*) as n_records

from "doordash"."main_core"."fct_ab_resultados"
where ab_group is not null
group by ab_group
having count(*) > 1


