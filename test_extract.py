"""
Quick test script to verify extraction works
Run: python test_extract.py
"""

from src.extract import DataExtractor


def test_extraction():
    """Test that we can extract all data"""
    print("🧪 Testing data extraction...\n")
    
    extractor = DataExtractor()
    data = extractor.extract_all()
    
    # Basic checks
    assert len(data['users']) > 0, "No users loaded!"
    assert len(data['subscriptions']) > 0, "No subscriptions loaded!"
    assert len(data['events']) > 0, "No events loaded!"
    
    print("\n✅ All extraction tests passed!")
    print(f"   - {len(data['users'])} users")
    print(f"   - {len(data['subscriptions'])} subscriptions")
    print(f"   - {len(data['events'])} events")


if __name__ == '__main__':
    test_extraction()