-- Teste singular: falha (retorna linhas) se grupo B não for mais rápido que grupo A.
-- O novo algoritmo de atribuição (grupo B) deve reduzir o tempo médio de entrega.
with metricas as (
    select
        ab_group,
        avg(tempo_total_min) as media
    from {{ ref('fct_entregas') }}
    group by ab_group
),

grupo_a as (select media from metricas where ab_group = 'A'),
grupo_b as (select media from metricas where ab_group = 'B')

select 'FALHOU: Grupo B não é mais rápido que Grupo A' as motivo
from grupo_a, grupo_b
where grupo_b.media >= grupo_a.media
