select
    date_trunc('month', order_date)     as month,
    region_name,
    nation_name,
    count(distinct order_id)            as order_count,
    count(distinct customer_id)         as customer_count,
    sum(total_revenue)                  as total_revenue,
    avg(total_revenue)                  as avg_order_revenue
from {{ ref('fct_orders') }}
group by 1, 2, 3
order by 1, 2, 3