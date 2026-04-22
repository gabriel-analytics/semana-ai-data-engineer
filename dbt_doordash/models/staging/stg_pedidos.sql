with source as (
    select * from {{ source('doordash_raw', 'doordash_clean') }}
),

renamed as (
    select
        cast(order_id as varchar) as order_id,
        cast(created_at as timestamp) as created_at,
        cast(customer_id as varchar) as customer_id,
        cast(restaurant_id as varchar) as restaurant_id,
        cast(ab_group as varchar) as ab_group,
        cast(status as varchar) as status,
        cast(total_amount_usd as decimal(10,2)) as total_amount_usd,
        cast(customer_city as varchar) as customer_city,
        cast(customer_segment as varchar) as customer_segment,
        cast(restaurant_name as varchar) as restaurant_name,
        cast(restaurant_category as varchar) as restaurant_category,
        cast(restaurant_city as varchar) as restaurant_city,
        cast(delivery_id as varchar) as delivery_id,
        cast(dasher_id as varchar) as dasher_id,
        cast(dasher_assigned_at as timestamp) as dasher_assigned_at,
        cast(pickup_at as timestamp) as pickup_at,
        cast(delivered_at as timestamp) as delivered_at,
        cast(delivery_duration_minutes as decimal(6,2)) as delivery_duration_minutes,
        cast(stage_1_order_placed_at as timestamp) as stage_1_order_placed_at,
        cast(stage_2_restaurant_confirmed_at as timestamp) as stage_2_restaurant_confirmed_at,
        cast(stage_3_dasher_assigned_at as timestamp) as stage_3_dasher_assigned_at,
        cast(stage_4_dasher_arrived_restaurant_at as timestamp) as stage_4_dasher_arrived_restaurant_at,
        cast(stage_5_order_picked_up_at as timestamp) as stage_5_order_picked_up_at,
        cast(stage_6_dasher_near_customer_at as timestamp) as stage_6_dasher_near_customer_at,
        cast(stage_7_delivered_at as timestamp) as stage_7_delivered_at,
        cast(hour_of_day as integer) as hour_of_day,
        cast(month as varchar) as month,
        cast(delivery_stage_bucket as varchar) as delivery_stage_bucket,
        -- Flags de qualidade do dado
        cast(has_duplicate_flag as boolean) as has_duplicate_flag,
        cast(has_timestamp_issue_flag as boolean) as has_timestamp_issue_flag,
        cast(has_missing_dasher_flag as boolean) as has_missing_dasher_flag,
        cast(has_outlier_flag as boolean) as has_outlier_flag,
        -- Flags derivadas
        status = 'delivered' as is_delivered,
        status = 'cancelled' as is_cancelled
    from source
    where order_id is not null
)

select * from renamed
