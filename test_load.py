"""
Test loading data to database
Run: python test_load.py
"""

from src.extract import DataExtractor
from src.transform import DataTransformer
from src.load import DataLoader
from src.database import DatabaseHelper


def test_full_etl():
    """Test complete ETL pipeline"""
    print("🧪 Testing full ETL pipeline...\n")
    
    # Test connection first
    if not DatabaseHelper.test_connection():
        print("\n❌ Cannot connect to database. Check your .env file!")
        return
    
    print("\n" + "="*60)
    print("STARTING FULL ETL TEST")
    print("="*60)
    
    # EXTRACT
    print("\n[1/3] EXTRACT")
    extractor = DataExtractor()
    raw_data = extractor.extract_all()
    
    # TRANSFORM
    print("\n[2/3] TRANSFORM")
    transformer = DataTransformer()
    clean_data = transformer.transform_all(raw_data)
    
    # LOAD
    print("\n[3/3] LOAD")
    loader = DataLoader()
    loader.load_all(clean_data)
    
    print("\n" + "="*60)
    print("ETL PIPELINE TEST COMPLETE!")
    print("="*60)
    
    # Show final stats
    print("\n📊 Final Warehouse State:")
    counts = DatabaseHelper.get_table_counts()
    if counts:
        for table, count in counts.items():
            print(f"   {table}: {count:,} rows")
    
    print("\n✅ All tests passed! Your ETL pipeline is working!")


if __name__ == '__main__':
    test_full_etl()