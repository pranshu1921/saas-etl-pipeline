-- =====================================================
-- SaaS ETL Pipeline - Database Schema
-- Simple star schema for subscription analytics
-- =====================================================

-- Clean slate
DROP TABLE IF EXISTS fact_subscriptions CASCADE;
DROP TABLE IF EXISTS dim_users CASCADE;
DROP TABLE IF EXISTS dim_plans CASCADE;
DROP TABLE IF EXISTS dim_dates CASCADE;

-- =====================================================
-- DIMENSION: Users
-- =====================================================

CREATE TABLE dim_users (
    user_key SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE,
    email VARCHAR(255),
    signup_date DATE,
    company_size VARCHAR(20),
    industry VARCHAR(50)
);

-- =====================================================
-- DIMENSION: Plans
-- =====================================================

CREATE TABLE dim_plans (
    plan_key SERIAL PRIMARY KEY,
    plan_id VARCHAR(20) UNIQUE,
    plan_name VARCHAR(50),
    monthly_price DECIMAL(10,2)
);

-- Insert standard plans
INSERT INTO dim_plans (plan_id, plan_name, monthly_price) VALUES
('free', 'Free', 0.00),
('pro', 'Pro', 29.00),
('enterprise', 'Enterprise', 99.00);

-- =====================================================
-- DIMENSION: Dates
-- =====================================================

CREATE TABLE dim_dates (
    date_key INTEGER PRIMARY KEY,
    date DATE UNIQUE,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    day_of_week VARCHAR(10)
);

-- Generate last 2 years + next year
INSERT INTO dim_dates (date_key, date, year, month, quarter, day_of_week)
SELECT 
    TO_CHAR(d, 'YYYYMMDD')::INTEGER,
    d::DATE,
    EXTRACT(YEAR FROM d)::INTEGER,
    EXTRACT(MONTH FROM d)::INTEGER,
    EXTRACT(QUARTER FROM d)::INTEGER,
    TO_CHAR(d, 'Day')
FROM generate_series('2023-01-01'::DATE, '2026-12-31'::DATE, '1 day') d;

-- =====================================================
-- FACT: Subscriptions
-- =====================================================

CREATE TABLE fact_subscriptions (
    sub_key SERIAL PRIMARY KEY,
    user_key INTEGER REFERENCES dim_users(user_key),
    plan_key INTEGER REFERENCES dim_plans(plan_key),
    date_key INTEGER REFERENCES dim_dates(date_key),
    
    event_type VARCHAR(20),  -- signup, upgrade, downgrade, cancel
    mrr_amount DECIMAL(10,2)
);

-- Indexes for common queries
CREATE INDEX idx_fact_user ON fact_subscriptions(user_key);
CREATE INDEX idx_fact_date ON fact_subscriptions(date_key);
CREATE INDEX idx_fact_event ON fact_subscriptions(event_type);

-- =====================================================
-- Quick verification
-- =====================================================

SELECT 'dim_users' as table_name, COUNT(*) FROM dim_users
UNION ALL
SELECT 'dim_plans', COUNT(*) FROM dim_plans
UNION ALL
SELECT 'dim_dates', COUNT(*) FROM dim_dates
UNION ALL
SELECT 'fact_subscriptions', COUNT(*) FROM fact_subscriptions;