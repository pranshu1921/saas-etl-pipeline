"""
Transform module - cleans data and applies business logic
Calculates MRR, identifies churn, enriches data
"""

import pandas as pd
from datetime import datetime


class DataTransformer:
    """Handles all data transformations"""
    
    def __init__(self):
        # Plan pricing lookup
        self.plan_prices = {
            'free': 0.00,
            'pro': 29.00,
            'enterprise': 99.00
        }
    
    def clean_users(self, users_df):
        """Clean and validate user data"""
        print("\n🧹 Cleaning users data...")
        
        df = users_df.copy()
        
        # Remove duplicates
        original_count = len(df)
        df = df.drop_duplicates(subset=['user_id'])
        if len(df) < original_count:
            print(f"   Removed {original_count - len(df)} duplicate users")
        
        # Convert dates
        df['signup_date'] = pd.to_datetime(df['signup_date'])
        
        # Fill missing values
        df['company_size'] = df['company_size'].fillna('unknown')
        df['industry'] = df['industry'].fillna('unknown')
        
        # Lowercase emails for consistency
        df['email'] = df['email'].str.lower()
        
        print(f"✅ Cleaned {len(df)} users")
        return df
    
    def clean_subscriptions(self, subs_df):
        """Clean and validate subscription data"""
        print("\n🧹 Cleaning subscriptions data...")
        
        df = subs_df.copy()
        
        # Remove duplicates
        original_count = len(df)
        df = df.drop_duplicates(subset=['subscription_id'])
        if len(df) < original_count:
            print(f"   Removed {original_count - len(df)} duplicate subscriptions")
        
        # Convert dates
        df['event_date'] = pd.to_datetime(df['event_date'])
        
        # Validate event types
        valid_events = ['signup', 'upgrade', 'downgrade', 'cancel']
        df = df[df['event_type'].isin(valid_events)]
        
        # Validate plan IDs
        valid_plans = ['free', 'pro', 'enterprise']
        df = df[df['plan_id'].isin(valid_plans)]
        
        print(f"✅ Cleaned {len(df)} subscription events")
        return df
    
    def calculate_mrr(self, subs_df):
        """Calculate MRR for each subscription event"""
        print("\n💰 Calculating MRR...")
        
        df = subs_df.copy()
        
        # Add MRR based on plan
        df['mrr_amount'] = df['plan_id'].map(self.plan_prices)
        
        # For cancellations, MRR should be 0
        df.loc[df['event_type'] == 'cancel', 'mrr_amount'] = 0
        
        print(f"✅ Calculated MRR for {len(df)} events")
        print(f"   Total MRR: ${df[df['event_type'] != 'cancel']['mrr_amount'].sum():,.2f}")
        
        return df
    
    def enrich_with_date_key(self, df, date_column='event_date'):
        """Add date_key in YYYYMMDD format"""
        df['date_key'] = df[date_column].dt.strftime('%Y%m%d').astype(int)
        return df
    
    def validate_data(self, users_df, subs_df):
        """Run basic data quality checks"""
        print("\n🔍 Running data quality checks...")
        
        issues = []
        
        # Check for nulls in critical fields
        if users_df['user_id'].isnull().any():
            issues.append("NULL user_ids found in users")
        
        if subs_df['subscription_id'].isnull().any():
            issues.append("NULL subscription_ids found")
        
        # Check for orphaned subscriptions (user not in users table)
        user_ids = set(users_df['user_id'])
        sub_user_ids = set(subs_df['user_id'])
        orphaned = sub_user_ids - user_ids
        
        if orphaned:
            issues.append(f"Found {len(orphaned)} subscriptions with no matching user")
            print(f"   ⚠️  {len(orphaned)} orphaned subscriptions (will be filtered)")
        
        # Check for future dates
        today = pd.Timestamp.now()
        future_subs = subs_df[subs_df['event_date'] > today]
        if len(future_subs) > 0:
            issues.append(f"Found {len(future_subs)} subscriptions with future dates")
        
        if not issues:
            print("✅ All data quality checks passed!")
        else:
            print(f"⚠️  Found {len(issues)} data quality issues:")
            for issue in issues:
                print(f"   - {issue}")
        
        return issues
    
    def transform_all(self, data):
        """Run all transformations"""
        print("\n" + "="*50)
        print("TRANSFORM PHASE")
        print("="*50)
        
        # Clean data
        users_clean = self.clean_users(data['users'])
        subs_clean = self.clean_subscriptions(data['subscriptions'])
        
        # Calculate metrics
        subs_with_mrr = self.calculate_mrr(subs_clean)
        
        # Add date keys
        subs_with_mrr = self.enrich_with_date_key(subs_with_mrr, 'event_date')
        users_clean = self.enrich_with_date_key(users_clean, 'signup_date')
        
        # Validate
        self.validate_data(users_clean, subs_with_mrr)
        
        # Filter out orphaned subscriptions
        user_ids = set(users_clean['user_id'])
        subs_with_mrr = subs_with_mrr[subs_with_mrr['user_id'].isin(user_ids)]
        
        print("\n✅ Transformation complete!")
        
        return {
            'users': users_clean,
            'subscriptions': subs_with_mrr
        }


# Test the transformer
if __name__ == '__main__':
    from extract import DataExtractor
    
    print("🧪 Testing transformation...")
    
    # Extract data
    extractor = DataExtractor()
    raw_data = extractor.extract_all()
    
    # Transform data
    transformer = DataTransformer()
    clean_data = transformer.transform_all(raw_data)
    
    print("\n📊 Transformed Data Preview:")
    print("\nUsers:")
    print(clean_data['users'].head())
    print("\nSubscriptions with MRR:")
    print(clean_data['subscriptions'].head())
    
    print("\n💡 MRR Breakdown by Plan:")
    mrr_by_plan = clean_data['subscriptions'][
        clean_data['subscriptions']['event_type'] != 'cancel'
    ].groupby('plan_id')['mrr_amount'].sum()
    print(mrr_by_plan)