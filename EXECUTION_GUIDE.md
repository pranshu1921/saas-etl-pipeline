# 🚀 Execution Guide

How to run the ETL pipeline and work with the data.

## Quick Commands

### Run Full Pipeline
```bash
python main.py
```

### Test Individual Components
```bash
# Test extraction only
python test_extract.py

# Test transformation only
python test_transform.py

# Test loading only
python test_load.py
```

### Database Operations
```bash
# Connect to database
psql -d saas_db

# Run metric queries
psql -d saas_db -f sql/metrics.sql

# View table counts
python src/database.py
```

---

## Understanding the Pipeline

### What Happens When You Run `python main.py`

1. **EXTRACT** - Reads data from files
   - `data/sample/users.csv`
   - `data/sample/subscriptions.json`
   - `data/sample/events.json`

2. **TRANSFORM** - Cleans and enriches data
   - Removes duplicates
   - Validates data quality
   - Calculates MRR
   - Adds date keys

3. **LOAD** - Inserts into database
   - `dim_users` table
   - `fact_subscriptions` table
   - Handles foreign key lookups

---

## Working with Your Own Data

### Using Custom Data Files

Replace the sample files with your own:

**data/sample/users.csv**
```csv
user_id,email,signup_date,company_size,industry
U021,newuser@example.com,2024-10-01,small,Technology
```

**data/sample/subscriptions.json**
```json
[
  {
    "subscription_id": "SUB026",
    "user_id": "U021",
    "plan_id": "pro",
    "event_type": "signup",
    "event_date": "2024-10-01"
  }
]
```

Then run:
```bash
python main.py
```

---

## Running Queries

### Total MRR
```sql
SELECT SUM(mrr_amount) as total_mrr
FROM fact_subscriptions
WHERE event_type != 'cancel';
```

### Active Users by Plan
```sql
SELECT 
    p.plan_name,
    COUNT(DISTINCT f.user_key) as users,
    SUM(f.mrr_amount) as mrr
FROM fact_subscriptions f
JOIN dim_plans p ON f.plan_key = p.plan_key
WHERE f.event_type != 'cancel'
GROUP BY p.plan_name;
```

### Monthly Signups
```sql
SELECT 
    d.year,
    d.month,
    COUNT(*) as signups
FROM fact_subscriptions f
JOIN dim_dates d ON f.date_key = d.date_key
WHERE f.event_type = 'signup'
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
```

### Churn Analysis
```sql
SELECT 
    COUNT(*) FILTER (WHERE event_type = 'cancel') as churned,
    COUNT(DISTINCT user_key) as total_users,
    ROUND(100.0 * COUNT(*) FILTER (WHERE event_type = 'cancel') / 
          COUNT(DISTINCT user_key), 2) as churn_rate_pct
FROM fact_subscriptions;
```

---

## Clearing Data

### Clear All Data (for fresh start)
```python
from src.database import DatabaseHelper

DatabaseHelper.clear_all_data()
```

### Or via SQL
```bash
psql -d saas_db
```
```sql
DELETE FROM fact_subscriptions;
DELETE FROM dim_users;
```

---

## Scheduled Runs

### Run Daily with Cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 2 AM
0 2 * * * cd /path/to/saas-etl-pipeline && python main.py >> logs/etl.log 2>&1
```

### Run with Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, time)
4. Action: Start a program
5. Program: `python`
6. Arguments: `main.py`
7. Start in: `C:\path\to\saas-etl-pipeline`

---

## Performance Tips

### For Large Data Files

1. **Process in Batches**
```python
   # In extract.py, add:
   chunk_size = 1000
   for chunk in pd.read_csv(file, chunksize=chunk_size):
       process(chunk)
```

2. **Use COPY Instead of INSERT**
```python
   # For bulk loading
   cursor.copy_from(file, 'table_name', sep=',')
```

3. **Create Indexes After Loading**
```sql
   -- Load data first, then:
   CREATE INDEX idx_name ON table(column);
```

---

## Monitoring

### Check Pipeline Status
```bash
# View logs
tail -f logs/etl.log

# Check last run time
ls -lt | head
```

### Set Up Alerts
```python
# In main.py, add:
if not success:
    send_email_alert("ETL Failed!")
```

---

## Development Workflow

### Making Changes

1. **Modify Code**
```bash
   # Edit src/transform.py
   vim src/transform.py
```

2. **Test Changes**
```bash
   python test_transform.py
```

3. **Run Full Pipeline**
```bash
   python main.py
```

4. **Verify Results**
```bash
   psql -d saas_db -f sql/metrics.sql
```

---

## Export Results

### Export to CSV
```bash
psql -d saas_db -c "COPY (SELECT * FROM vw_mrr_summary) TO STDOUT WITH CSV HEADER" > mrr_export.csv
```

### Export Metrics
```bash
psql -d saas_db -f sql/metrics.sql > results.txt
```

---

## Common Workflows

### Weekly Data Refresh
```bash
#!/bin/bash
# weekly_refresh.sh

echo "Starting weekly ETL..."
cd /path/to/saas-etl-pipeline

# Backup current data
pg_dump saas_db > backups/saas_db_$(date +%Y%m%d).sql

# Clear old data
python -c "from src.database import DatabaseHelper; DatabaseHelper.clear_all_data()"

# Run pipeline with new data
python main.py

echo "Weekly ETL complete!"
```

### Generate Monthly Report
```bash
#!/bin/bash
# monthly_report.sh

psql -d saas_db -f sql/metrics.sql > reports/report_$(date +%Y%m).txt
echo "Report generated: reports/report_$(date +%Y%m).txt"
```

---

## Next Steps

1. ✅ Run the pipeline successfully
2. ✅ Explore the data
3. ✅ Write custom queries
4. ✅ Add your own data
5. ✅ Customize transformations
6. ✅ Build dashboards (connect to Tableau/PowerBI)

---

**Happy Data Engineering!** 🎉