# Troubleshooting Guide

## Common Issues

### 1. "Cannot connect to database"

**Problem:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env` file
- Test connection: `psql -d saas_db`
- Make sure database exists: `createdb saas_db`

### 2. "Table does not exist"

**Problem:** `relation "dim_users" does not exist`

**Solution:**
```bash
psql -d saas_db -f sql/schema.sql
```

### 3. "No such file or directory"

**Problem:** Can't find data files

**Solution:**
- Make sure you're in the project root directory
- Check files exist: `ls data/sample/`
- Files should be: `users.csv`, `subscriptions.json`, `events.json`

### 4. "Permission denied"

**Problem:** Can't write to database

**Solutions:**
- Check PostgreSQL user permissions
- Make sure you're using correct DB_USER in .env
- Try with postgres superuser

### 5. "Module not found"

**Problem:** `ModuleNotFoundError: No module named 'pandas'`

**Solution:**
```bash
pip install -r requirements.txt
```

## Verification Steps

### 1. Test Database Connection
```bash
python src/database.py
```

### 2. Test Extract
```bash
python test_extract.py
```

### 3. Test Transform
```bash
python test_transform.py
```

### 4. Test Load
```bash
python test_load.py
```

### 5. Run Full Pipeline
```bash
python main.py
```

## Clearing Data (for testing)
```python
from src.database import DatabaseHelper

DatabaseHelper.clear_all_data()
```

## Getting Help

If you're still stuck:
1. Check PostgreSQL logs
2. Verify Python version (3.8+)
3. Make sure all files are in correct locations
4. Try running test scripts one by one