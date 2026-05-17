test_cases_content = '''version: 1
test_cases:

  - id: E001
    difficulty: easy
    category: aggregation
    question: "How many customers do we have?"
    gold_sql: |
      SELECT COUNT(DISTINCT customer_id) as total_customers
      FROM agg_customer_stats

  - id: E002
    difficulty: easy
    category: aggregation
    question: "What is the total number of orders?"
    gold_sql: |
      SELECT COUNT(DISTINCT order_id) as total_orders
      FROM fct_orders

  - id: E003
    difficulty: easy
    category: aggregation
    question: "What is the total revenue across all orders?"
    gold_sql: |
      SELECT SUM(total_revenue) as total_revenue
      FROM fct_orders

  - id: E004
    difficulty: easy
    category: filter
    question: "How many orders are currently open?"
    gold_sql: |
      SELECT COUNT(DISTINCT order_id) as open_orders
      FROM fct_orders
      WHERE order_status = 'O'

  - id: E005
    difficulty: easy
    category: aggregation
    question: "How many customers are in the AUTOMOBILE market segment?"
    gold_sql: |
      SELECT COUNT(DISTINCT customer_id) as customer_count
      FROM agg_customer_stats
      WHERE market_segment = 'AUTOMOBILE'

  - id: E006
    difficulty: easy
    category: ranking
    question: "Who are the top 5 customers by lifetime revenue?"
    gold_sql: |
      SELECT customer_name, lifetime_revenue
      FROM agg_customer_stats
      ORDER BY lifetime_revenue DESC
      LIMIT 5

  - id: E007
    difficulty: easy
    category: aggregation
    question: "What is the total revenue by region?"
    gold_sql: |
      SELECT region_name, SUM(total_revenue) as total_revenue
      FROM fct_orders
      GROUP BY region_name
      ORDER BY total_revenue DESC

  - id: E008
    difficulty: easy
    category: aggregation
    question: "How many customers are in each market segment?"
    gold_sql: |
      SELECT market_segment, COUNT(DISTINCT customer_id) as customer_count
      FROM agg_customer_stats
      GROUP BY market_segment
      ORDER BY customer_count DESC

  - id: E009
    difficulty: easy
    category: filter
    question: "What is the total revenue from the ASIA region?"
    gold_sql: |
      SELECT SUM(total_revenue) as total_revenue
      FROM fct_orders
      WHERE region_name = 'ASIA'

  - id: E010
    difficulty: easy
    category: aggregation
    question: "What is the average order value?"
    gold_sql: |
      SELECT AVG(total_revenue) as avg_order_value
      FROM fct_orders

  - id: E011
    difficulty: easy
    category: ranking
    question: "What are the top 5 nations by total revenue?"
    gold_sql: |
      SELECT nation_name, SUM(total_revenue) as total_revenue
      FROM fct_orders
      GROUP BY nation_name
      ORDER BY total_revenue DESC
      LIMIT 5

  - id: E012
    difficulty: easy
    category: filter
    question: "How many urgent orders do we have?"
    gold_sql: |
      SELECT COUNT(DISTINCT order_id) as urgent_orders
      FROM fct_orders
      WHERE order_priority = '1-URGENT'

  - id: E013
    difficulty: easy
    category: aggregation
    question: "What is the average lifetime revenue per customer?"
    gold_sql: |
      SELECT AVG(lifetime_revenue) as avg_lifetime_revenue
      FROM agg_customer_stats

  - id: E014
    difficulty: easy
    category: aggregation
    question: "How many orders came from each region?"
    gold_sql: |
      SELECT region_name, COUNT(DISTINCT order_id) as order_count
      FROM fct_orders
      GROUP BY region_name
      ORDER BY order_count DESC

  - id: E015
    difficulty: easy
    category: filter
    question: "What is the total revenue from EUROPE?"
    gold_sql: |
      SELECT SUM(total_revenue) as total_revenue
      FROM fct_orders
      WHERE region_name = 'EUROPE'

  - id: M001
    difficulty: medium
    category: time_series
    question: "What was the total revenue by month in 1995?"
    gold_sql: |
      SELECT month, SUM(total_revenue) as total_revenue
      FROM agg_monthly_revenue
      WHERE month >= '1995-01-01' AND month < '1996-01-01'
      GROUP BY month
      ORDER BY month ASC

  - id: M002
    difficulty: medium
    category: time_series
    question: "How has monthly revenue trended in the EUROPE region?"
    gold_sql: |
      SELECT month, SUM(total_revenue) as total_revenue
      FROM agg_monthly_revenue
      WHERE region_name = 'EUROPE'
      GROUP BY month
      ORDER BY month ASC

  - id: M003
    difficulty: medium
    category: aggregation
    question: "What is the revenue breakdown by market segment?"
    gold_sql: |
      SELECT market_segment,
             COUNT(DISTINCT customer_id) as customer_count,
             SUM(lifetime_revenue) as total_revenue
      FROM agg_customer_stats
      GROUP BY market_segment
      ORDER BY total_revenue DESC

  - id: M004
    difficulty: medium
    category: filter
    question: "Who are the top 10 customers in the BUILDING segment?"
    gold_sql: |
      SELECT customer_name, nation_name, lifetime_revenue
      FROM agg_customer_stats
      WHERE market_segment = 'BUILDING'
      ORDER BY lifetime_revenue DESC
      LIMIT 10

  - id: M005
    difficulty: medium
    category: time_series
    question: "What was total revenue in 1996?"
    gold_sql: |
      SELECT SUM(total_revenue) as total_revenue
      FROM agg_monthly_revenue
      WHERE month >= '1996-01-01' AND month < '1997-01-01'

  - id: M006
    difficulty: medium
    category: aggregation
    question: "What is the average order value by region?"
    gold_sql: |
      SELECT region_name, AVG(total_revenue) as avg_order_value
      FROM fct_orders
      GROUP BY region_name
      ORDER BY avg_order_value DESC

  - id: M007
    difficulty: medium
    category: time_series
    question: "How many orders were placed each year?"
    gold_sql: |
      SELECT date_trunc('year', order_date) as year,
             COUNT(DISTINCT order_id) as order_count
      FROM fct_orders
      GROUP BY year
      ORDER BY year ASC

  - id: M008
    difficulty: medium
    category: filter
    question: "What is the total revenue from fulfilled orders in ASIA?"
    gold_sql: |
      SELECT SUM(total_revenue) as total_revenue
      FROM fct_orders
      WHERE order_status = 'F'
      AND region_name = 'ASIA'

  - id: M009
    difficulty: medium
    category: ranking
    question: "Which nation has the highest average order value?"
    gold_sql: |
      SELECT nation_name, AVG(total_revenue) as avg_order_value
      FROM fct_orders
      GROUP BY nation_name
      ORDER BY avg_order_value DESC
      LIMIT 1

  - id: M010
    difficulty: medium
    category: aggregation
    question: "What percentage of orders are fulfilled vs open?"
    gold_sql: |
      SELECT order_status,
             COUNT(order_id) as order_count,
             ROUND(100.0 * COUNT(order_id) / SUM(COUNT(order_id)) OVER (), 2) as percentage
      FROM fct_orders
      GROUP BY order_status
      ORDER BY order_count DESC

  - id: M011
    difficulty: medium
    category: time_series
    question: "What was the best month for revenue in 1994?"
    gold_sql: |
      SELECT month, SUM(total_revenue) as total_revenue
      FROM agg_monthly_revenue
      WHERE month >= '1994-01-01' AND month < '1995-01-01'
      GROUP BY month
      ORDER BY total_revenue DESC
      LIMIT 1

  - id: M012
    difficulty: medium
    category: filter
    question: "How many customers are based in GERMANY?"
    gold_sql: |
      SELECT COUNT(DISTINCT customer_id) as customer_count
      FROM agg_customer_stats
      WHERE nation_name = 'GERMANY'

  - id: M013
    difficulty: medium
    category: aggregation
    question: "What is the total revenue by nation in the ASIA region?"
    gold_sql: |
      SELECT nation_name, SUM(total_revenue) as total_revenue
      FROM fct_orders
      WHERE region_name = 'ASIA'
      GROUP BY nation_name
      ORDER BY total_revenue DESC

  - id: M014
    difficulty: medium
    category: ranking
    question: "Which market segment has the highest average order value?"
    gold_sql: |
      SELECT market_segment, AVG(avg_order_value) as avg_order_value
      FROM agg_customer_stats
      GROUP BY market_segment
      ORDER BY avg_order_value DESC
      LIMIT 1

  - id: M015
    difficulty: medium
    category: time_series
    question: "What was the monthly order count in 1993?"
    gold_sql: |
      SELECT month, SUM(order_count) as order_count
      FROM agg_monthly_revenue
      WHERE month >= '1993-01-01' AND month < '1994-01-01'
      GROUP BY month
      ORDER BY month ASC

  - id: M016
    difficulty: medium
    category: filter
    question: "What is the total revenue from urgent high priority orders?"
    gold_sql: |
      SELECT SUM(total_revenue) as total_revenue
      FROM fct_orders
      WHERE order_priority = '1-URGENT'

  - id: M017
    difficulty: medium
    category: aggregation
    question: "How many distinct nations do our customers come from?"
    gold_sql: |
      SELECT COUNT(DISTINCT nation_name) as nation_count
      FROM agg_customer_stats

  - id: M018
    difficulty: medium
    category: ranking
    question: "What are the top 3 regions by order count?"
    gold_sql: |
      SELECT region_name, COUNT(DISTINCT order_id) as order_count
      FROM fct_orders
      GROUP BY region_name
      ORDER BY order_count DESC
      LIMIT 3

  - id: M019
    difficulty: medium
    category: filter
    question: "Which customers have placed more than 30 orders?"
    gold_sql: |
      SELECT customer_name, nation_name, total_orders, lifetime_revenue
      FROM agg_customer_stats
      WHERE total_orders > 30
      ORDER BY total_orders DESC

  - id: M020
    difficulty: medium
    category: time_series
    question: "What was the total revenue in the first quarter of 1995?"
    gold_sql: |
      SELECT SUM(total_revenue) as total_revenue
      FROM agg_monthly_revenue
      WHERE month >= '1995-01-01' AND month < '1995-04-01'

  - id: H001
    difficulty: hard
    category: window
    question: "What is the revenue rank of each region?"
    gold_sql: |
      SELECT region_name,
             SUM(total_revenue) as total_revenue,
             RANK() OVER (ORDER BY SUM(total_revenue) DESC) as revenue_rank
      FROM fct_orders
      GROUP BY region_name

  - id: H002
    difficulty: hard
    category: time_series
    question: "What was the year over year revenue growth from 1993 to 1994?"
    gold_sql: |
      SELECT
        SUM(CASE WHEN month >= '1993-01-01' AND month < '1994-01-01' THEN total_revenue END) as revenue_1993,
        SUM(CASE WHEN month >= '1994-01-01' AND month < '1995-01-01' THEN total_revenue END) as revenue_1994,
        ROUND(100.0 * (
          SUM(CASE WHEN month >= '1994-01-01' AND month < '1995-01-01' THEN total_revenue END) -
          SUM(CASE WHEN month >= '1993-01-01' AND month < '1994-01-01' THEN total_revenue END)
        ) / SUM(CASE WHEN month >= '1993-01-01' AND month < '1994-01-01' THEN total_revenue END), 2) as yoy_growth_pct
      FROM agg_monthly_revenue

  - id: H003
    difficulty: hard
    category: window
    question: "What is the running total revenue by month in 1995?"
    gold_sql: |
      WITH monthly AS (
        SELECT month,
               SUM(total_revenue) as total_revenue
        FROM agg_monthly_revenue
        WHERE month >= '1995-01-01' AND month < '1996-01-01'
        GROUP BY month
      )
      SELECT month,
             total_revenue,
             SUM(total_revenue) OVER (ORDER BY month) as running_total
      FROM monthly
      ORDER BY month ASC

  - id: H004
    difficulty: hard
    category: filter
    question: "Which customers have a lifetime revenue above the average?"
    gold_sql: |
      SELECT customer_name, market_segment, nation_name, lifetime_revenue
      FROM agg_customer_stats
      WHERE lifetime_revenue > (SELECT AVG(lifetime_revenue) FROM agg_customer_stats)
      ORDER BY lifetime_revenue DESC

  - id: H005
    difficulty: hard
    category: aggregation
    question: "What is the revenue contribution percentage of each nation within its region?"
    gold_sql: |
      SELECT region_name,
             nation_name,
             SUM(total_revenue) as nation_revenue,
             ROUND(100.0 * SUM(total_revenue) / SUM(SUM(total_revenue)) OVER (PARTITION BY region_name), 2) as pct_of_region
      FROM fct_orders
      GROUP BY region_name, nation_name
      ORDER BY region_name, nation_revenue DESC

  - id: H006
    difficulty: hard
    category: time_series
    question: "Which month had the highest revenue in each year?"
    gold_sql: |
      WITH monthly AS (
        SELECT date_trunc('year', month) as year,
               month,
               SUM(total_revenue) as total_revenue,
               RANK() OVER (PARTITION BY date_trunc('year', month) ORDER BY SUM(total_revenue) DESC) as rnk
        FROM agg_monthly_revenue
        GROUP BY year, month
      )
      SELECT year, month, total_revenue
      FROM monthly
      WHERE rnk = 1
      ORDER BY year

  - id: H007
    difficulty: hard
    category: window
    question: "What is the month over month revenue change in 1996?"
    gold_sql: |
      WITH monthly AS (
        SELECT month,
               SUM(total_revenue) as total_revenue
        FROM agg_monthly_revenue
        WHERE month >= '1996-01-01' AND month < '1997-01-01'
        GROUP BY month
      )
      SELECT month,
             total_revenue,
             LAG(total_revenue) OVER (ORDER BY month) as prev_month_revenue,
             ROUND(total_revenue - LAG(total_revenue) OVER (ORDER BY month), 2) as revenue_change
      FROM monthly
      ORDER BY month

  - id: H008
    difficulty: hard
    category: aggregation
    question: "What is the average number of orders per customer by market segment?"
    gold_sql: |
      SELECT market_segment,
             AVG(total_orders) as avg_orders_per_customer,
             COUNT(DISTINCT customer_id) as customer_count
      FROM agg_customer_stats
      GROUP BY market_segment
      ORDER BY avg_orders_per_customer DESC

  - id: H009
    difficulty: hard
    category: filter
    question: "Which nations have more than 1000 customers?"
    gold_sql: |
      SELECT nation_name,
             COUNT(DISTINCT customer_id) as customer_count,
             SUM(lifetime_revenue) as total_revenue
      FROM agg_customer_stats
      GROUP BY nation_name
      HAVING COUNT(DISTINCT customer_id) > 1000
      ORDER BY customer_count DESC

  - id: H010
    difficulty: hard
    category: time_series
    question: "What was the total revenue in the second half of 1997?"
    gold_sql: |
      SELECT SUM(total_revenue) as total_revenue
      FROM agg_monthly_revenue
      WHERE month >= '1997-07-01' AND month < '1998-01-01'

  - id: H011
    difficulty: hard
    category: window
    question: "Rank customers by lifetime revenue within each market segment?"
    gold_sql: |
      SELECT customer_name,
             market_segment,
             lifetime_revenue,
             RANK() OVER (PARTITION BY market_segment ORDER BY lifetime_revenue DESC) as segment_rank
      FROM agg_customer_stats
      ORDER BY market_segment, segment_rank
      LIMIT 25

  - id: H012
    difficulty: hard
    category: aggregation
    question: "What is the revenue per customer by region?"
    gold_sql: |
      SELECT region_name,
             SUM(total_revenue) as total_revenue,
             COUNT(DISTINCT customer_id) as customer_count,
             ROUND(SUM(total_revenue) / COUNT(DISTINCT customer_id), 2) as revenue_per_customer
      FROM fct_orders
      GROUP BY region_name
      ORDER BY revenue_per_customer DESC

  - id: H013
    difficulty: hard
    category: filter
    question: "Which customers placed their first order after 1995?"
    gold_sql: |
      SELECT customer_name, nation_name, market_segment, first_order_date, lifetime_revenue
      FROM agg_customer_stats
      WHERE first_order_date > '1995-12-31'
      ORDER BY first_order_date ASC

  - id: H014
    difficulty: hard
    category: aggregation
    question: "What is the ratio of open to fulfilled orders by region?"
    gold_sql: |
      SELECT region_name,
             SUM(CASE WHEN order_status = 'O' THEN 1 ELSE 0 END) as open_orders,
             SUM(CASE WHEN order_status = 'F' THEN 1 ELSE 0 END) as fulfilled_orders,
             ROUND(1.0 * SUM(CASE WHEN order_status = 'O' THEN 1 ELSE 0 END) /
                   SUM(CASE WHEN order_status = 'F' THEN 1 ELSE 0 END), 4) as open_to_fulfilled_ratio
      FROM fct_orders
      GROUP BY region_name
      ORDER BY open_to_fulfilled_ratio DESC

  - id: H015
    difficulty: hard
    category: window
    question: "What is the cumulative customer count by market segment ordered by lifetime revenue?"
    gold_sql: |
      SELECT market_segment,
             customer_name,
             lifetime_revenue,
             SUM(COUNT(*)) OVER (PARTITION BY market_segment ORDER BY lifetime_revenue DESC) as cumulative_customers
      FROM agg_customer_stats
      GROUP BY market_segment, customer_name, lifetime_revenue
      ORDER BY market_segment, lifetime_revenue DESC
      LIMIT 20
'''

with open("evals/test_cases/test_cases.yaml", "w") as f:
    f.write(test_cases_content)

print("✅ test_cases.yaml written successfully")

# Verify it loads
import yaml
with open("evals/test_cases/test_cases.yaml") as f:
    data = yaml.safe_load(f)

print(f"✅ Loaded {len(data['test_cases'])} test cases")