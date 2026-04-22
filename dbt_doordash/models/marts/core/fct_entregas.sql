with int_etapas as (
    select * from {{ ref('int_pedidos_com_etapas') }}
),

fct as (
    select
        order_id,
        created_at,
        ab_group,
        customer_city,
        customer_segment,
        restaurant_category,
        delivery_duration_minutes as tempo_total_min,
        duracao_aceite_min,
        duracao_preparo_min,
        duracao_atribuicao_min,
        duracao_coleta_min,
        duracao_rota_min,
        duracao_proximidade_min,
        hour_of_day,
        month,
        delivery_stage_bucket,
        total_amount_usd,

        -- Classificação de velocidade de entrega
        case
            when delivery_duration_minutes < 30 then 'rapida'
            when delivery_duration_minutes between 30 and 45 then 'normal'
            else 'lenta'
        end as classificacao_entrega,

        -- Flag de entrega no horário de pico
        case
            when hour_of_day between 11 and 14 then true
            when hour_of_day between 18 and 22 then true
            else false
        end as is_horario_pico

    from int_etapas
)

select * from fct
