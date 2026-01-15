# 💼 SaaS ETL Pipeline

A simple ETL pipeline that processes subscription data for a SaaS business. Built to demonstrate ETL concepts and data warehousing fundamentals.

## What This Does

Takes subscription data from CSV/JSON files and loads it into a PostgreSQL database for analytics:
- **Extract**: Read CSV and JSON files
- **Transform**: Clean data and calculate metrics
- **Load**: Put data into a star schema warehouse

## The Business Case

Imagine a SaaS company called "CloudTask" that offers project management software with 3 plans:
- Free ($0/month)
- Pro ($29/month)  
- Enterprise ($99/month)

This pipeline helps answer questions like:
- How much recurring revenue do we have? (MRR)
- How many customers cancel each month? (Churn)
- Which plans are most popular?

## Tech Stack

- **Python 3.8+** - ETL scripts
- **PostgreSQL** - Data warehouse
- **pandas** - Data processing

## Project Structure
```
saas-etl-pipeline/
├── README.md
├── requirements.txt
├── .env.example
├── sql/
│   ├── schema.sql          # Creates all tables
│   └── metrics.sql         # Helpful metric queries
├── data/
│   └── sample/             # Sample CSV/JSON files
├── src/
│   ├── extract.py          # Read files
│   ├── transform.py        # Clean & transform
│   └── load.py             # Load to database
└── main.py                 # Run everything
```

## Quick Setup
```bash
# 1. Create database
createdb saas_db

# 2. Create tables
psql -d saas_db -f sql/schema.sql

# 3. Install Python packages
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your database info

# 5. Run the pipeline
python main.py
```

## What I Learned Building This

- Star schema design for analytics
- ETL patterns (staging → warehouse)
- SaaS business metrics (MRR, churn, LTV)
- Python + PostgreSQL integration
- Data quality and validation

## Sample Data

The `data/sample/` folder has example files:
- `users.csv` - Customer signups
- `subscriptions.json` - Plan changes
- `events.json` - Usage data

## Database Schema

Simple star schema with:
- **fact_subscriptions** - All subscription events
- **dim_users** - Customer info
- **dim_plans** - Plan details
- **dim_dates** - Date dimension

See `sql/schema.sql` for details.

## Author

[Your Name]  
Built to demonstrate ETL and data warehousing skills  
GitHub: [@yourusername](https://github.com/yourusername)
```

---

#### File: `.gitignore`
```
# Python
__pycache__/
*.pyc
venv/
env/

# Environment
.env

# Data
data/sample/*.csv
data/sample/*.json
!data/sample/.gitkeep

# Logs
*.log

# IDE
.vscode/
.DS_Store
```

---

#### File: `.env.example`
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=saas_db
DB_USER=postgres
DB_PASSWORD=your_password
```

---

#### File: `requirements.txt`
```
pandas==2.0.3
psycopg2-binary==2.9.9
python-dotenv==1.0.0