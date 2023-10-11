with VIP_customers as (
    select
        customer_id,
        last_name || ', ' || first_name as customer_name,
        number_of_orders
    from {{ ref('customers') }}
),

AVG_ORDER_COUNT as (
    select
        avg(number_of_orders) as avg_order_count
    from {{ ref('customers') }}
    where number_of_orders is not null
),

final as (
    select
        customer_id,
        customer_name,
        number_of_orders
    from VIP_customers
    join AVG_ORDER_COUNT
        on number_of_orders > (avg_order_count + 1)
)

select * from final
