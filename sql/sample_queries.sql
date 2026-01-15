-- =====================================================
-- Sample Queries for SaaS Metrics
-- Useful queries to analyze subscription data
-- =====================================================

-- =====================================================
-- 1. CURRENT STATE METRICS
-- =====================================================

-- Active Users and MRR
SELECT 
    COUNT(DISTINCT user_key) as active_users,
    SUM(mrr_amount) as total_mrr,
    ROUND(AVG(mrr_amount), 2) as avg_revenue_per_user
FROM fact_subscriptions
WHERE event_type != 'cancel';

-- Plan Distribution
SELECT 
    p.plan_name,
    COUNT(DISTINCT f.user_key) as active_users,
    ROUND(100.0 * COUNT(DISTINCT f.user_key) / 
        SUM(COUNT(DISTINCT f.user_key)) OVER (), 2) as pct_of_users,
    SUM(f.mrr_amount) as total_mrr
FROM fact_subscriptions f
JOIN dim_plans p ON f.plan_key = p.plan_key
WHERE f.event_type != 'cancel'
GROUP BY p.plan_name
ORDER BY total_mrr DESC;

-- =====================================================
-- 2. GROWTH METRICS
-- =====================================================

-- Monthly Signups Trend
SELECT 
    d.year,
    d.month,
    TO_CHAR(d.date, 'Mon YYYY') as month_name,
    COUNT(*) as new_signups
FROM fact_subscriptions f
JOIN dim_dates d ON f.date_key = d.date_key
WHERE f.event_type = 'signup'
GROUP BY d.year, d.month, TO_CHAR(d.date, 'Mon YYYY')
ORDER BY d.year, d.month;

-- MRR Growth by Month
SELECT 
    d.year,
    d.month,
    SUM(CASE WHEN f.event_type = 'signup' THEN f.mrr_amount ELSE 0 END) as new_mrr,
    SUM(CASE WHEN f.event_type = 'upgrade' THEN f.mrr_amount ELSE 0 END) as expansion_mrr,
    SUM(CASE WHEN f.event_type = 'downgrade' THEN -f.mrr_amount ELSE 0 END) as contraction_mrr,
    SUM(CASE WHEN f.event_type = 'cancel' THEN -f.mrr_amount ELSE 0 END) as churned_mrr,
    SUM(
        CASE WHEN f.event_type = 'signup' THEN f.mrr_amount ELSE 0 END +
        CASE WHEN f.event_type = 'upgrade' THEN f.mrr_amount ELSE 0 END -
        CASE WHEN f.event_type = 'downgrade' THEN f.mrr_amount ELSE 0 END -
        CASE WHEN f.event_type = 'cancel' THEN f.mrr_amount ELSE 0 END
    ) as net_new_mrr
FROM fact_subscriptions f
JOIN dim_dates d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- =====================================================
-- 3. CUSTOMER BEHAVIOR
-- =====================================================

-- User Journey (signup to current state)
SELECT 
    u.user_id,
    u.email,
    u.signup_date,
    u.company_size,
    COUNT(f.sub_key) as total_events,
    MAX(CASE WHEN f.event_type = 'signup' THEN p.plan_name END) as initial_plan,
    STRING_AGG(f.event_type || ':' || p.plan_name, ' → ' ORDER BY f.date_key) as journey
FROM dim_users u
JOIN fact_subscriptions f ON u.user_key = f.user_key
JOIN dim_plans p ON f.plan_key = p.plan_key
GROUP BY u.user_id, u.email, u.signup_date, u.company_size
ORDER BY u.signup_date DESC
LIMIT 10;

-- Upgrade/Downgrade Analysis
SELECT 
    event_type,
    COUNT(*) as event_count,
    ROUND(AVG(mrr_amount), 2) as avg_mrr_impact
FROM fact_subscriptions
WHERE event_type IN ('upgrade', 'downgrade')
GROUP BY event_type;

-- =====================================================
-- 4. CHURN ANALYSIS
-- =====================================================

-- Churn Rate
WITH active_users AS (
    SELECT COUNT(DISTINCT user_key) as total
    FROM fact_subscriptions
    WHERE event_type != 'cancel'
),
churned_users AS (
    SELECT COUNT(DISTINCT user_key) as total
    FROM fact_subscriptions
    WHERE event_type = 'cancel'
)
SELECT 
    a.total as active_users,
    c.total as churned_users,
    ROUND(100.0 * c.total / (a.total + c.total), 2) as churn_rate_pct
FROM active_users a, churned_users c;

-- Churned Users by Plan
SELECT 
    p.plan_name,
    COUNT(*) as churned_count,
    SUM(f.mrr_amount) as lost_mrr
FROM fact_subscriptions f
JOIN dim_plans p ON f.plan_key = p.plan_key
WHERE f.event_type = 'cancel'
GROUP BY p.plan_name
ORDER BY lost_mrr DESC;

-- =====================================================
-- 5. COHORT ANALYSIS
-- =====================================================

-- Signup Cohorts by Month
SELECT 
    DATE_TRUNC('month', u.signup_date)::DATE as cohort_month,
    COUNT(DISTINCT u.user_key) as cohort_size,
    COUNT(DISTINCT CASE 
        WHEN f.event_type != 'cancel' 
        THEN f.user_key 
    END) as still_active,
    ROUND(100.0 * COUNT(DISTINCT CASE 
        WHEN f.event_type != 'cancel' 
        THEN f.user_key 
    END) / COUNT(DISTINCT u.user_key), 2) as retention_rate_pct
FROM dim_users u
LEFT JOIN fact_subscriptions f ON u.user_key = f.user_key
GROUP BY DATE_TRUNC('month', u.signup_date)::DATE
ORDER BY cohort_month DESC;

-- =====================================================
-- 6. INDUSTRY INSIGHTS
-- =====================================================

-- MRR by Industry
SELECT 
    u.industry,
    COUNT(DISTINCT u.user_key) as customers,
    SUM(f.mrr_amount) as total_mrr,
    ROUND(AVG(f.mrr_amount), 2) as avg_mrr_per_customer
FROM dim_users u
JOIN fact_subscriptions f ON u.user_key = f.user_key
WHERE f.event_type != 'cancel'
GROUP BY u.industry
ORDER BY total_mrr DESC;

-- Company Size Distribution
SELECT 
    u.company_size,
    COUNT(DISTINCT u.user_key) as customers,
    SUM(f.mrr_amount) as total_mrr
FROM dim_users u
JOIN fact_subscriptions f ON u.user_key = f.user_key
WHERE f.event_type != 'cancel'
GROUP BY u.company_size
ORDER BY total_mrr DESC;

-- =====================================================
-- 7. QUICK SUMMARY DASHBOARD
-- =====================================================

-- One-page business summary
SELECT 
    'Total MRR' as metric,
    '$' || ROUND(SUM(mrr_amount), 2) as value
FROM fact_subscriptions
WHERE event_type != 'cancel'

UNION ALL

SELECT 
    'Active Users',
    COUNT(DISTINCT user_key)::TEXT
FROM fact_subscriptions
WHERE event_type != 'cancel'

UNION ALL

SELECT 
    'ARPU (Avg Revenue Per User)',
    '$' || ROUND(AVG(mrr_amount), 2)
FROM fact_subscriptions
WHERE event_type != 'cancel'

UNION ALL

SELECT 
    'Total Signups',
    COUNT(*)::TEXT
FROM fact_subscriptions
WHERE event_type = 'signup'

UNION ALL

SELECT 
    'Total Cancellations',
    COUNT(*)::TEXT
FROM fact_subscriptions
WHERE event_type = 'cancel';