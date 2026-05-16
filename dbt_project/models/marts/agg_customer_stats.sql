select
    c.customer_id,
    c.customer_name,
    c.market_segment,
    c.account_balance,
    n.nation_name,
    r.region_name,
    count(distinct o.order_id)          as total_orders,
    sum(o.total_revenue)                as lifetime_revenue,
    avg(o.total_revenue)                as avg_order_value,
    min(o.order_date)                   as first_order_date,
    max(o.order_date)                   as last_order_date
from {{ ref('stg_customers') }} c
left join {{ ref('stg_nations') }} n
    on c.nation_id = n.nation_id
left join {{ ref('stg_regions') }} r
    on n.region_id = r.region_id
left join {{ ref('fct_orders') }} o
    on c.customer_id = o.customer_id
group by 1, 2, 3, 4, 5, 6