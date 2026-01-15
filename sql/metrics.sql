-- ================================================
-- METRICS VIEWS
-- Pre-computed SaaS metrics for dashboards
-- ================================================

-- ================================================
-- VIEW: MRR Trend
-- Monthly Recurring Revenue by month
-- ================================================

CREATE OR REPLACE VIEW vw_mrr_trend AS
WITH monthly_mrr AS (
    SELECT 
        d.year,
        d.month,
        TO_CHAR(d.full_date, 'YYYY-MM') as month_key,
        DATE_TRUNC('month', d.full_date)::DATE as month_start,
        
        -- New MRR (new signups)
        SUM(CASE 
            WHEN f.event_type = 'signup' AND f.is_new_customer = TRUE 
            THEN f.monthly_value 
            ELSE 0 
        END) as new_mrr,
        
        -- Expansion MRR (upgrades)
        SUM(CASE 
            WHEN f.event_type = 'upgrade' 
            THEN f.monthly_value 
            ELSE 0 
        END) as expansion_mrr,
        
        -- Contraction MRR (downgrades)
        SUM(CASE 
            WHEN f.event_type = 'downgrade' 
            THEN -1 * f.monthly_value 
            ELSE 0 
        END) as contraction_mrr,
        
        -- Churned MRR (cancellations)
        SUM(CASE 
            WHEN f.event_type = 'cancel' 
            THEN -1 * f.monthly_value 
            ELSE 0 
        END) as churned_mrr,
        
        -- Total active MRR
        SUM(f.monthly_value) as total_mrr
        
    FROM fact_subscriptions f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month, TO_CHAR(d.full_date, 'YYYY-MM'), DATE_TRUNC('month', d.full_date)
)
SELECT 
    month_key,
    month_start,
    ROUND(new_mrr, 2) as new_mrr,
    ROUND(expansion_mrr, 2) as expansion_mrr,
    ROUND(contraction_mrr, 2) as contraction_mrr,
    ROUND(churned_mrr, 2) as churned_mrr,
    ROUND(new_mrr + expansion_mrr + contraction_mrr + churned_mrr, 2) as net_new_mrr,
    ROUND(total_mrr, 2) as total_mrr
FROM monthly_mrr
ORDER BY month_start DESC;

COMMENT ON VIEW vw_mrr_trend IS 'Monthly MRR breakdown by component';

-- ================================================
-- VIEW: Churn Rate
-- Monthly customer churn analysis
-- ================================================

CREATE OR REPLACE VIEW vw_churn_rate AS
WITH monthly_stats AS (
    SELECT 
        d.year,
        d.month,
        TO_CHAR(d.full_date, 'YYYY-MM') as month_key,
        DATE_TRUNC('month', d.full_date)::DATE as month_start,
        
        -- Active customers at start of month
        COUNT(DISTINCT CASE WHEN d.day_of_month = 1 THEN f.user_key END) as active_start,
        
        -- Churned customers
        COUNT(DISTINCT CASE WHEN f.event_type = 'cancel' THEN f.user_key END) as churned_customers,
        
        -- New customers
        COUNT(DISTINCT CASE WHEN f.event_type = 'signup' THEN f.user_key END) as new_customers
        
    FROM fact_subscriptions f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month, TO_CHAR(d.full_date, 'YYYY-MM'), DATE_TRUNC('month', d.full_date)
)
SELECT 
    month_key,
    month_start,
    active_start,
    new_customers,
    churned_customers,
    CASE 
        WHEN active_start > 0 
        THEN ROUND((churned_customers::NUMERIC / active_start * 100), 2)
        ELSE 0 
    END as churn_rate_pct,
    CASE 
        WHEN active_start > 0 
        THEN ROUND(((active_start - churned_customers)::NUMERIC / active_start * 100), 2)
        ELSE 0 
    END as retention_rate_pct
FROM monthly_stats
WHERE active_start > 0
ORDER BY month_start DESC;

COMMENT ON VIEW vw_churn_rate IS 'Monthly churn and retention rates';

-- ================================================
-- VIEW: Plan Distribution
-- Current active subscriptions by plan
-- ================================================

CREATE OR REPLACE VIEW vw_plan_distribution AS
SELECT 
    p.plan_name,
    COUNT(DISTINCT f.user_key) as active_users,
    ROUND(COUNT(DISTINCT f.user_key)::NUMERIC / SUM(COUNT(DISTINCT f.user_key)) OVER () * 100, 2) as pct_of_total,
    ROUND(SUM(f.monthly_value), 2) as total_mrr,
    ROUND(AVG(f.monthly_value), 2) as avg_revenue_per_user
FROM fact_subscriptions f
JOIN dim_plans p ON f.plan_key = p.plan_key
WHERE f.event_type NOT IN ('cancel')
    AND f.event_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.plan_name
ORDER BY total_mrr DESC;

COMMENT ON VIEW vw_plan_distribution IS 'Active subscription distribution by plan';

-- ================================================
-- VIEW: Customer Lifetime Value
-- Estimated LTV by cohort
-- ================================================

CREATE OR REPLACE VIEW vw_customer_ltv AS
WITH customer_metrics AS (
    SELECT 
        u.user_key,
        u.user_id,
        u.signup_date,
        DATE_TRUNC('month', u.signup_date)::DATE as cohort_month,
        SUM(f.monthly_value) as total_revenue,
        COUNT(DISTINCT DATE_TRUNC('month', f.event_date)) as months_active,
        MAX(f.event_date) as last_activity_date
    FROM dim_users u
    JOIN fact_subscriptions f ON u.user_key = f.user_key
    WHERE f.event_type != 'cancel'
    GROUP BY u.user_key, u.user_id, u.signup_date
)
SELECT 
    cohort_month,
    COUNT(DISTINCT user_key) as cohort_size,
    ROUND(AVG(total_revenue), 2) as avg_revenue_per_customer,
    ROUND(AVG(months_active), 1) as avg_months_active,
    ROUND(AVG(total_revenue / NULLIF(months_active, 0)), 2) as avg_monthly_value,
    ROUND(AVG(total_revenue) * 3, 2) as estimated_36m_ltv
FROM customer_metrics
GROUP BY cohort_month
ORDER BY cohort_month DESC;

COMMENT ON VIEW vw_customer_ltv IS 'Customer lifetime value by cohort';

-- ================================================
-- Verify views created
-- ================================================

SELECT 
    viewname,
    definition IS NOT NULL as has_definition
FROM pg_views
WHERE schemaname = 'public'
    AND viewname LIKE 'vw_%'
ORDER BY viewname;