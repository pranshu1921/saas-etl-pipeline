"""
Main ETL Pipeline Orchestrator
Run: python main.py
"""

from src.extract import DataExtractor
from src.transform import DataTransformer
from src.load import DataLoader
from src.database import DatabaseHelper
from datetime import datetime


def run_etl_pipeline():
    """Execute full ETL pipeline"""
    
    start_time = datetime.now()
    
    print("\n" + "="*60)
    print("🚀 SaaS ETL PIPELINE")
    print("="*60)
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Step 1: Extract
        print("STEP 1: EXTRACT DATA")
        print("-" * 60)
        extractor = DataExtractor()
        raw_data = extractor.extract_all()
        
        # Step 2: Transform
        print("\nSTEP 2: TRANSFORM DATA")
        print("-" * 60)
        transformer = DataTransformer()
        clean_data = transformer.transform_all(raw_data)
        
        # Step 3: Load
        print("\nSTEP 3: LOAD TO WAREHOUSE")
        print("-" * 60)
        loader = DataLoader()
        loader.load_all(clean_data)
        
        # Success!
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*60)
        print("✅ ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ETL PIPELINE FAILED")
        print("="*60)
        print(f"Error: {e}")
        return False


if __name__ == '__main__':
    success = run_etl_pipeline()
    
    if success:
        print("\n💡 Next steps:")
        print("   1. Connect to database: psql -d saas_db")
        print("   2. Run metric queries: psql -d saas_db -f sql/metrics.sql")
        print("   3. Explore the data!")
    else:
        print("\n💡 Troubleshooting:")
        print("   1. Check database connection in .env")
        print("   2. Verify tables exist: psql -d saas_db -f sql/schema.sql")
        print("   3. Check logs for errors")
```

---

#### File: `.env.example` (Updated with comments)
```
# ================================================
# Database Configuration
# Copy this file to .env and update with your info
# ================================================

DB_HOST=localhost
DB_PORT=5432
DB_NAME=saas_db
DB_USER=postgres
DB_PASSWORD=your_password

# ================================================
# Setup Instructions:
# 1. Create database: createdb saas_db
# 2. Run schema: psql -d saas_db -f sql/schema.sql
# 3. Copy this file: cp .env.example .env
# 4. Update DB_PASSWORD with your actual password
# 5. Run pipeline: python main.py
# ================================================