select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.order_status,
    o.order_priority,
    n.nation_name,
    r.region_name,
    count(l.line_number)        as line_item_count,
    sum(l.quantity)             as total_quantity,
    sum(l.revenue)              as total_revenue,
    sum(l.extended_price)       as total_extended_price,
    avg(l.discount)             as avg_discount
from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c
    on o.customer_id = c.customer_id
left join {{ ref('stg_nations') }} n
    on c.nation_id = n.nation_id
left join {{ ref('stg_regions') }} r
    on n.region_id = r.region_id
left join {{ ref('stg_lineitems') }} l
    on o.order_id = l.order_id
group by 1, 2, 3, 4, 5, 6, 7