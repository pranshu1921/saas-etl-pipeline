"""
Test transformation logic
Run: python test_transform.py
"""

from src.extract import DataExtractor
from src.transform import DataTransformer


def test_transformation():
    """Test the full transformation pipeline"""
    print("🧪 Testing data transformation...\n")
    
    # Extract
    extractor = DataExtractor()
    raw_data = extractor.extract_all()
    
    # Transform
    transformer = DataTransformer()
    clean_data = transformer.transform_all(raw_data)
    
    # Verify results
    users = clean_data['users']
    subs = clean_data['subscriptions']
    
    print("\n📊 Transformation Results:")
    print(f"   Users: {len(users)} records")
    print(f"   Subscriptions: {len(subs)} records")
    
    # Check MRR calculation
    total_mrr = subs[subs['event_type'] != 'cancel']['mrr_amount'].sum()
    print(f"   Total MRR: ${total_mrr:,.2f}")
    
    # Check date keys added
    assert 'date_key' in users.columns, "date_key not added to users"
    assert 'date_key' in subs.columns, "date_key not added to subscriptions"
    
    # Check MRR values
    assert 'mrr_amount' in subs.columns, "mrr_amount not calculated"
    assert subs['mrr_amount'].notna().all(), "NULL MRR values found"
    
    print("\n✅ All transformation tests passed!")
    
    # Show sample MRR breakdown
    print("\n💰 MRR Breakdown by Plan:")
    mrr_summary = subs[subs['event_type'] != 'cancel'].groupby('plan_id').agg({
        'user_id': 'count',
        'mrr_amount': 'sum'
    }).rename(columns={'user_id': 'count', 'mrr_amount': 'total_mrr'})
    print(mrr_summary)
    
    # Show event type distribution
    print("\n📈 Event Distribution:")
    event_dist = subs['event_type'].value_counts()
    print(event_dist)


if __name__ == '__main__':
    test_transformation()