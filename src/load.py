"""
Load module - loads transformed data into PostgreSQL warehouse
Handles dimension and fact table loading
"""

import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from config import config


class DataLoader:
    """Loads data into the data warehouse"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to PostgreSQL database"""
        print("\n🔌 Connecting to database...")
        
        try:
            self.conn = psycopg2.connect(config.db_connection_string)
            self.cursor = self.conn.cursor()
            print("✅ Connected to database")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Disconnected from database")
    
    def load_users(self, users_df):
        """Load users into dim_users table"""
        print("\n📥 Loading users to dim_users...")
        
        # Prepare data for insertion
        users_data = [
            (
                row['user_id'],
                row['email'],
                row['signup_date'],
                row['company_size'],
                row['industry']
            )
            for _, row in users_df.iterrows()
        ]
        
        # Insert with conflict handling (upsert)
        query = """
            INSERT INTO dim_users (user_id, email, signup_date, company_size, industry)
            VALUES %s
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                email = EXCLUDED.email,
                company_size = EXCLUDED.company_size,
                industry = EXCLUDED.industry,
                updated_at = CURRENT_TIMESTAMP
        """
        
        try:
            execute_values(self.cursor, query, users_data)
            self.conn.commit()
            print(f"✅ Loaded {len(users_data)} users")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error loading users: {e}")
            raise
    
    def get_user_keys(self, user_ids):
        """Get user_key for given user_ids"""
        query = """
            SELECT user_id, user_key
            FROM dim_users
            WHERE user_id = ANY(%s)
        """
        
        self.cursor.execute(query, (list(user_ids),))
        results = self.cursor.fetchall()
        
        # Return as dictionary
        return {user_id: user_key for user_id, user_key in results}
    
    def get_plan_keys(self, plan_ids):
        """Get plan_key for given plan_ids"""
        query = """
            SELECT plan_id, plan_key
            FROM dim_plans
            WHERE plan_id = ANY(%s)
        """
        
        self.cursor.execute(query, (list(plan_ids),))
        results = self.cursor.fetchall()
        
        # Return as dictionary
        return {plan_id: plan_key for plan_id, plan_key in results}
    
    def load_subscriptions(self, subs_df):
        """Load subscriptions into fact_subscriptions table"""
        print("\n📥 Loading subscriptions to fact_subscriptions...")
        
        # Get user keys
        user_ids = subs_df['user_id'].unique()
        user_key_map = self.get_user_keys(user_ids)
        
        # Get plan keys
        plan_ids = subs_df['plan_id'].unique()
        plan_key_map = self.get_plan_keys(plan_ids)
        
        # Add foreign keys to dataframe
        subs_df['user_key'] = subs_df['user_id'].map(user_key_map)
        subs_df['plan_key'] = subs_df['plan_id'].map(plan_key_map)
        
        # Check for any missing keys
        missing_users = subs_df['user_key'].isna().sum()
        missing_plans = subs_df['plan_key'].isna().sum()
        
        if missing_users > 0:
            print(f"   ⚠️  {missing_users} subscriptions with missing user keys (skipped)")
            subs_df = subs_df.dropna(subset=['user_key'])
        
        if missing_plans > 0:
            print(f"   ⚠️  {missing_plans} subscriptions with missing plan keys (skipped)")
            subs_df = subs_df.dropna(subset=['plan_key'])
        
        # Prepare data for insertion
        subs_data = [
            (
                int(row['user_key']),
                int(row['plan_key']),
                row['date_key'],
                row['event_type'],
                row['mrr_amount']
            )
            for _, row in subs_df.iterrows()
        ]
        
        # Insert data
        query = """
            INSERT INTO fact_subscriptions (user_key, plan_key, date_key, event_type, mrr_amount)
            VALUES %s
        """
        
        try:
            execute_values(self.cursor, query, subs_data)
            self.conn.commit()
            print(f"✅ Loaded {len(subs_data)} subscription events")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error loading subscriptions: {e}")
            raise
    
    def get_load_statistics(self):
        """Get row counts from all tables"""
        print("\n📊 Warehouse Statistics:")
        
        tables = ['dim_users', 'dim_plans', 'dim_dates', 'fact_subscriptions']
        
        for table in tables:
            query = f"SELECT COUNT(*) FROM {table}"
            self.cursor.execute(query)
            count = self.cursor.fetchone()[0]
            print(f"   {table}: {count:,} rows")
    
    def verify_data_quality(self):
        """Run basic data quality checks after loading"""
        print("\n🔍 Running post-load data quality checks...")
        
        # Check for orphaned subscriptions
        query = """
            SELECT COUNT(*)
            FROM fact_subscriptions f
            LEFT JOIN dim_users u ON f.user_key = u.user_key
            WHERE u.user_key IS NULL
        """
        self.cursor.execute(query)
        orphaned = self.cursor.fetchone()[0]
        
        if orphaned > 0:
            print(f"   ⚠️  {orphaned} orphaned subscriptions found!")
        else:
            print("   ✅ No orphaned subscriptions")
        
        # Check total MRR
        query = """
            SELECT 
                COUNT(DISTINCT user_key) as active_users,
                SUM(mrr_amount) as total_mrr
            FROM fact_subscriptions
            WHERE event_type != 'cancel'
        """
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        print(f"   ✅ Active users: {result[0]}")
        print(f"   ✅ Total MRR: ${result[1]:,.2f}")
    
    def load_all(self, data):
        """Load all data to warehouse"""
        print("\n" + "="*50)
        print("LOAD PHASE")
        print("="*50)
        
        try:
            # Connect
            self.connect()
            
            # Load dimensions
            self.load_users(data['users'])
            
            # Load facts
            self.load_subscriptions(data['subscriptions'])
            
            # Verify
            self.get_load_statistics()
            self.verify_data_quality()
            
            print("\n✅ Load complete!")
            
        finally:
            # Always disconnect
            self.disconnect()


# Test the loader
if __name__ == '__main__':
    from extract import DataExtractor
    from transform import DataTransformer
    
    print("🧪 Testing load pipeline...\n")
    
    # Extract
    extractor = DataExtractor()
    raw_data = extractor.extract_all()
    
    # Transform
    transformer = DataTransformer()
    clean_data = transformer.transform_all(raw_data)
    
    # Load
    loader = DataLoader()
    loader.load_all(clean_data)
    
    print("\n✅ Full ETL test complete!")