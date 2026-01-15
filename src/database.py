"""
Database utilities and helper functions
"""

import psycopg2
from config import config


class DatabaseHelper:
    """Helper functions for database operations"""
    
    @staticmethod
    def test_connection():
        """Test database connection"""
        print("🔌 Testing database connection...")
        
        try:
            conn = psycopg2.connect(config.db_connection_string)
            cursor = conn.cursor()
            
            # Run simple query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            print(f"✅ Connected successfully!")
            print(f"   PostgreSQL version: {version[:50]}...")
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    @staticmethod
    def clear_all_data():
        """Clear all data from warehouse (for testing)"""
        print("🗑️  Clearing all warehouse data...")
        
        try:
            conn = psycopg2.connect(config.db_connection_string)
            cursor = conn.cursor()
            
            # Clear in order (facts first, then dimensions)
            cursor.execute("DELETE FROM fact_subscriptions;")
            cursor.execute("DELETE FROM dim_users;")
            
            conn.commit()
            
            print("✅ All data cleared")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            raise
    
    @staticmethod
    def get_table_counts():
        """Get row counts from all tables"""
        try:
            conn = psycopg2.connect(config.db_connection_string)
            cursor = conn.cursor()
            
            tables = ['dim_users', 'dim_plans', 'dim_dates', 'fact_subscriptions']
            counts = {}
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return counts
            
        except Exception as e:
            print(f"❌ Error getting counts: {e}")
            return None


# Quick connection test
if __name__ == '__main__':
    DatabaseHelper.test_connection()
    
    print("\n📊 Current table counts:")
    counts = DatabaseHelper.get_table_counts()
    if counts:
        for table, count in counts.items():
            print(f"   {table}: {count:,}")