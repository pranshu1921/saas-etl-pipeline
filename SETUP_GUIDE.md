# 🛠️ Setup Guide

Complete step-by-step instructions to get the ETL pipeline running on your machine.

## Prerequisites

Before you start, make sure you have:

- **PostgreSQL 13+** installed
- **Python 3.8+** installed
- **pip** package manager
- **Terminal/Command Prompt** access

## Step 1: Check Prerequisites (2 minutes)

### Verify PostgreSQL
```bash
psql --version
# Should show: psql (PostgreSQL) 13.x or higher
```

If not installed:
- **Mac:** `brew install postgresql`
- **Ubuntu:** `sudo apt-get install postgresql`
- **Windows:** Download from postgresql.org

### Verify Python
```bash
python3 --version
# Should show: Python 3.8.x or higher
```

---

## Step 2: Clone Project (1 minute)
```bash
git clone https://github.com/YOUR_USERNAME/saas-etl-pipeline.git
cd saas-etl-pipeline
```

---

## Step 3: Set Up Database (3 minutes)

### Create Database
```bash
createdb saas_db
```

### Verify Database Created
```bash
psql -l | grep saas_db
# Should show saas_db in the list
```

### Create Tables
```bash
psql -d saas_db -f sql/schema.sql
```

**Expected output:**
```
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
INSERT 0 3
CREATE TABLE
...
```

### Verify Tables Created
```bash
psql -d saas_db -c "\dt"
```

**Expected output:**
```
             List of relations
 Schema |        Name         | Type  |  Owner
--------+---------------------+-------+----------
 public | dim_dates           | table | postgres
 public | dim_plans           | table | postgres
 public | dim_users           | table | postgres
 public | fact_subscriptions  | table | postgres
```

---

## Step 4: Install Python Dependencies (2 minutes)
```bash
pip install -r requirements.txt
```

**Expected output:**
```
Collecting pandas==2.0.3
Collecting psycopg2-binary==2.9.9
Collecting python-dotenv==1.0.0
...
Successfully installed pandas-2.0.3 psycopg2-binary-2.9.9 python-dotenv-1.0.0
```

---

## Step 5: Configure Environment (1 minute)

### Copy Environment Template
```bash
cp .env.example .env
```

### Edit .env File
Open `.env` in your text editor and update:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=saas_db
DB_USER=postgres          # ← Your PostgreSQL username
DB_PASSWORD=your_password # ← Your PostgreSQL password
```

**Finding your PostgreSQL credentials:**
- Username is usually `postgres`
- Password is what you set during PostgreSQL installation
- If you don't remember, you may need to reset it

---

## Step 6: Test Connection (1 minute)
```bash
python src/database.py
```

**Expected output:**
```
🔌 Testing database connection...
✅ Connected successfully!
   PostgreSQL version: PostgreSQL 13.x...

📊 Current table counts:
   dim_users: 0
   dim_plans: 3
   dim_dates: 1,096
   fact_subscriptions: 0
```

If you see errors, check:
- PostgreSQL is running: `pg_isready`
- Credentials in `.env` are correct
- Database exists: `psql -l | grep saas_db`

---

## Step 7: Run ETL Pipeline (1 minute)
```bash
python main.py
```

**Expected output:**
```
============================================================
🚀 SaaS ETL PIPELINE
============================================================
Started at: 2026-01-15 10:30:00

STEP 1: EXTRACT DATA
------------------------------------------------------------
📖 Reading users from data/sample/users.csv
✅ Loaded 20 users
📖 Reading subscriptions from data/sample/subscriptions.json
✅ Loaded 25 subscription events
...

STEP 2: TRANSFORM DATA
------------------------------------------------------------
🧹 Cleaning users data...
✅ Cleaned 20 users
💰 Calculating MRR...
✅ Calculated MRR for 25 events
   Total MRR: $667.00
...

STEP 3: LOAD TO WAREHOUSE
------------------------------------------------------------
🔌 Connecting to database...
✅ Connected to database
📥 Loading users to dim_users...
✅ Loaded 20 users
📥 Loading subscriptions to fact_subscriptions...
✅ Loaded 25 subscription events
...

============================================================
✅ ETL PIPELINE COMPLETED SUCCESSFULLY!
============================================================
Duration: 2.34 seconds
```

---

## Step 8: Verify Data Loaded (1 minute)

### Check Row Counts
```bash
psql -d saas_db
```
```sql
SELECT COUNT(*) FROM dim_users;
-- Should show: 20

SELECT COUNT(*) FROM fact_subscriptions;
-- Should show: 25

\q  -- to quit
```

### Run Metric Queries
```bash
psql -d saas_db -f sql/metrics.sql
```

**Expected output:**
```
 total_mrr
-----------
    667.00
(1 row)

  plan_name  | customers |  mrr
-------------+-----------+--------
 Enterprise  |         5 | 495.00
 Pro         |        11 | 319.00
 Free        |         4 |   0.00
```

---

## ✅ Setup Complete!

You now have:
- ✅ PostgreSQL database with star schema
- ✅ Sample data loaded
- ✅ Working ETL pipeline
- ✅ Ability to run metric queries

---

## 🎯 What to Do Next

### Option 1: Explore the Data
```bash
psql -d saas_db
```
```sql
-- See all users
SELECT * FROM dim_users LIMIT 5;

-- See subscription events
SELECT * FROM fact_subscriptions LIMIT 10;

-- Calculate total MRR
SELECT SUM(mrr_amount) FROM fact_subscriptions WHERE event_type != 'cancel';
```

### Option 2: Modify and Re-run
```bash
# Edit data files in data/sample/
# Add more users or subscriptions

# Clear existing data
python -c "from src.database import DatabaseHelper; DatabaseHelper.clear_all_data()"

# Re-run pipeline
python main.py
```

### Option 3: Customize
- Add more data sources
- Create new transformations
- Build additional metrics
- Add more validation rules

---

## 🐛 Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

### Quick Fixes

**"Cannot connect to database"**
```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL if needed
brew services start postgresql  # Mac
sudo service postgresql start   # Linux
```

**"Table does not exist"**
```bash
# Recreate tables
psql -d saas_db -f sql/schema.sql
```

**"Module not found"**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📧 Getting Help

If you're stuck:
1. Check TROUBLESHOOTING.md
2. Review error messages carefully
3. Verify each step was completed
4. Try the test scripts individually

---

**Total Setup Time:** ~10-15 minutes

**You're ready to go!** 🚀