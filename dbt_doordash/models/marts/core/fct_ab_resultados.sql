with fct as (
    select * from {{ ref('fct_entregas') }}
),

-- Métricas por grupo
metricas_grupo as (
    select
        ab_group,
        count(*) as total_pedidos,
        round(avg(tempo_total_min), 2) as media_tempo_total_min,
        round(median(tempo_total_min), 2) as mediana_tempo_total_min,
        round(stddev(tempo_total_min), 2) as desvio_padrao_min,
        round(percentile_cont(0.05) within group (order by tempo_total_min), 2) as p5_tempo_min,
        round(percentile_cont(0.25) within group (order by tempo_total_min), 2) as p25_tempo_min,
        round(percentile_cont(0.75) within group (order by tempo_total_min), 2) as p75_tempo_min,
        round(percentile_cont(0.95) within group (order by tempo_total_min), 2) as p95_tempo_min,
        round(avg(duracao_aceite_min), 2) as media_aceite_min,
        round(avg(duracao_preparo_min), 2) as media_preparo_min,
        round(avg(duracao_atribuicao_min), 2) as media_atribuicao_min,
        round(avg(duracao_coleta_min), 2) as media_coleta_min,
        round(avg(duracao_rota_min), 2) as media_rota_min,
        round(sum(total_amount_usd), 2) as receita_total_usd,
        round(avg(total_amount_usd), 2) as ticket_medio_usd,
        count(case when classificacao_entrega = 'rapida' then 1 end) as entregas_rapidas,
        count(case when classificacao_entrega = 'lenta' then 1 end) as entregas_lentas,
        count(case when is_horario_pico = true then 1 end) as pedidos_horario_pico
    from fct
    group by ab_group
),

-- Cross join para calcular delta do grupo B vs controle A
grupo_a as (select * from metricas_grupo where ab_group = 'A'),
grupo_b as (select * from metricas_grupo where ab_group = 'B'),

delta as (
    select
        b.ab_group,
        b.total_pedidos,
        b.media_tempo_total_min,
        b.mediana_tempo_total_min,
        b.desvio_padrao_min,
        b.p5_tempo_min,
        b.p25_tempo_min,
        b.p75_tempo_min,
        b.p95_tempo_min,
        b.media_aceite_min,
        b.media_preparo_min,
        b.media_atribuicao_min,
        b.media_coleta_min,
        b.media_rota_min,
        b.receita_total_usd,
        b.ticket_medio_usd,
        b.entregas_rapidas,
        b.entregas_lentas,
        b.pedidos_horario_pico,
        round(b.media_tempo_total_min - a.media_tempo_total_min, 2) as delta_vs_controle_min,
        round(
            (b.media_tempo_total_min - a.media_tempo_total_min) / a.media_tempo_total_min * 100,
            2
        ) as delta_vs_controle_pct
    from grupo_b b
    cross join grupo_a a

    union all

    select
        a.ab_group,
        a.total_pedidos,
        a.media_tempo_total_min,
        a.mediana_tempo_total_min,
        a.desvio_padrao_min,
        a.p5_tempo_min,
        a.p25_tempo_min,
        a.p75_tempo_min,
        a.p95_tempo_min,
        a.media_aceite_min,
        a.media_preparo_min,
        a.media_atribuicao_min,
        a.media_coleta_min,
        a.media_rota_min,
        a.receita_total_usd,
        a.ticket_medio_usd,
        a.entregas_rapidas,
        a.entregas_lentas,
        a.pedidos_horario_pico,
        0.0 as delta_vs_controle_min,
        0.0 as delta_vs_controle_pct
    from grupo_a a
)

select * from delta
order by ab_group
