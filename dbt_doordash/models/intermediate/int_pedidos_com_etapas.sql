with stg as (
    select * from {{ ref('stg_pedidos') }}
    -- Apenas pedidos entregues, sem flags de dados problemáticos
    where is_delivered = true
      and has_missing_dasher_flag = false
      and has_timestamp_issue_flag = false
),

etapas as (
    select
        order_id,
        created_at,
        ab_group,
        customer_city,
        customer_segment,
        restaurant_category,
        delivery_duration_minutes,
        hour_of_day,
        month,
        delivery_stage_bucket,
        total_amount_usd,
        dasher_id,

        -- Etapa 1: Aceite (restaurante confirma o pedido)
        round(
            (epoch(stage_2_restaurant_confirmed_at) - epoch(stage_1_order_placed_at)) / 60.0,
            2
        ) as duracao_aceite_min,

        -- Etapa 2: Preparo (do aceite até entregador chegar no restaurante)
        round(
            (epoch(stage_4_dasher_arrived_restaurant_at) - epoch(stage_2_restaurant_confirmed_at)) / 60.0,
            2
        ) as duracao_preparo_min,

        -- Etapa 3: Atribuição do dasher (do pedido até dasher ser designado)
        round(
            (epoch(stage_3_dasher_assigned_at) - epoch(stage_1_order_placed_at)) / 60.0,
            2
        ) as duracao_atribuicao_min,

        -- Etapa 4: Coleta (dasher pega o pedido no restaurante)
        round(
            (epoch(stage_5_order_picked_up_at) - epoch(stage_4_dasher_arrived_restaurant_at)) / 60.0,
            2
        ) as duracao_coleta_min,

        -- Etapa 5: Rota (do pickup até entrega ao cliente)
        round(
            (epoch(stage_7_delivered_at) - epoch(stage_5_order_picked_up_at)) / 60.0,
            2
        ) as duracao_rota_min,

        -- Etapa 6: Proximidade (do aviso de chegada até entrega)
        round(
            (epoch(stage_7_delivered_at) - epoch(stage_6_dasher_near_customer_at)) / 60.0,
            2
        ) as duracao_proximidade_min,

        stage_1_order_placed_at,
        stage_2_restaurant_confirmed_at,
        stage_3_dasher_assigned_at,
        stage_4_dasher_arrived_restaurant_at,
        stage_5_order_picked_up_at,
        stage_6_dasher_near_customer_at,
        stage_7_delivered_at

    from stg
)

select * from etapas
