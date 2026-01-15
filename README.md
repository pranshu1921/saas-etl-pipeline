# 💼 SaaS ETL Pipeline

A simple ETL pipeline that processes subscription data for a SaaS business. Built to demonstrate ETL concepts, data warehousing, and SaaS metrics calculation.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)
![ETL](https://img.shields.io/badge/ETL-Pipeline-green.svg)

## What This Does

Takes subscription data from CSV/JSON files and loads it into a PostgreSQL database for analytics:
- **Extract**: Read CSV and JSON files
- **Transform**: Clean data and calculate MRR
- **Load**: Insert into star schema warehouse

## The Business Case

Imagine a SaaS company called "CloudTask" that offers project management software:
- **Free Plan** - $0/month
- **Pro Plan** - $29/month  
- **Enterprise Plan** - $99/month

This pipeline helps answer:
- 💰 How much recurring revenue do we have? (MRR)
- 📉 How many customers cancel each month? (Churn)
- 📈 Which plans are most popular?
- 🎯 What's our customer lifetime value?

## Quick Start
```bash
# 1. Create database
createdb saas_db
psql -d saas_db -f sql/schema.sql

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your database credentials

# 4. Run pipeline
python main.py
```

**Full setup:** See [SETUP_GUIDE.md](SETUP_GUIDE.md)

## Project Structure
```
saas-etl-pipeline/
├── README.md               # You are here
├── SETUP_GUIDE.md         # Detailed setup instructions
├── EXECUTION_GUIDE.md     # How to run and use
├── TROUBLESHOOTING.md     # Common issues
├── requirements.txt       # Python packages
├── .env.example          # Configuration template
│
├── sql/
│   ├── schema.sql        # Create all tables
│   ├── metrics.sql       # Business metric queries
│   └── sample_queries.sql # Example queries
│
├── src/
│   ├── extract.py        # Read CSV/JSON files
│   ├── transform.py      # Clean & calculate metrics
│   ├── load.py           # Insert into database
│   ├── database.py       # Database utilities
│   └── validator.py      # Data quality checks
│
├── data/sample/
│   ├── users.csv         # Sample user data
│   ├── subscriptions.json # Sample subscription events
│   └── events.json       # Sample usage events
│
├── test_extract.py       # Test extraction
├── test_transform.py     # Test transformation
├── test_load.py          # Test loading
└── main.py              # Run full pipeline
```

## Tech Stack

- **Python 3.8+** - ETL scripts
- **PostgreSQL** - Data warehouse
- **pandas** - Data processing
- **psycopg2** - Database connection

## Database Schema

Simple star schema:
- **fact_subscriptions** - All subscription events (signups, upgrades, cancels)
- **dim_users** - Customer information
- **dim_plans** - Plan details (Free, Pro, Enterprise)
- **dim_dates** - Date dimension

## Sample Metrics

### Total MRR
```sql
SELECT SUM(mrr_amount) FROM fact_subscriptions WHERE event_type != 'cancel';
```

### Churn Rate
```sql
SELECT 
    COUNT(*) FILTER (WHERE event_type = 'cancel') * 100.0 / 
    COUNT(DISTINCT user_key) as churn_rate_pct
FROM fact_subscriptions;
```

### Active Users by Plan
```sql
SELECT p.plan_name, COUNT(DISTINCT f.user_key) as users
FROM fact_subscriptions f
JOIN dim_plans p ON f.plan_key = p.plan_key
WHERE f.event_type != 'cancel'
GROUP BY p.plan_name;
```

More queries in [sql/sample_queries.sql](sql/sample_queries.sql)

## What I Learned

- ✅ Star schema design for analytics
- ✅ ETL patterns (Extract → Transform → Load)
- ✅ SaaS business metrics (MRR, Churn, LTV)
- ✅ Python + PostgreSQL integration
- ✅ Data quality validation
- ✅ Handling multiple data formats (CSV, JSON)

## Running Tests
```bash
# Test each component
python test_extract.py
python test_transform.py
python test_load.py

# Run full pipeline
python main.py
```

## Use Cases

This pipeline can be adapted for:
- Subscription businesses (SaaS, streaming, memberships)
- E-commerce recurring orders
- Membership organizations
- Any business with recurring revenue

## Future Enhancements

Potential additions:
- [ ] Automated data quality reports
- [ ] Email alerts on pipeline failures
- [ ] Dashboard integration (Tableau, Power BI)
- [ ] Incremental loading (only new data)
- [ ] More advanced metrics (cohort analysis, LTV prediction)
- [ ] API data sources
- [ ] Scheduling with Airflow

## Documentation

- 📖 [Setup Guide](SETUP_GUIDE.md) - Complete installation instructions
- 🚀 [Execution Guide](EXECUTION_GUIDE.md) - How to run and customize
- 🐛 [Troubleshooting](TROUBLESHOOTING.md) - Common issues and fixes
- 📝 [Notes](NOTES.md) - Development notes and decisions

## Author

**[Your Name]**  
GitHub: [@yourusername](https://github.com/yourusername)  
LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

Built to demonstrate ETL and data warehousing skills for data analyst/engineer roles.

## License

MIT License - see [LICENSE](LICENSE) for details

---

**⭐ If you find this helpful, please star it!**

**Last Updated:** January 2026
```

---

#### File: `logs/.gitkeep`
```
# Logs directory
# Log files will be created here