"""
Data validation utilities
Simple checks to ensure data quality
"""

import pandas as pd


class DataValidator:
    """Validates data quality"""
    
    @staticmethod
    def check_required_columns(df, required_columns, table_name):
        """Check if all required columns exist"""
        missing = [col for col in required_columns if col not in df.columns]
        
        if missing:
            raise ValueError(f"{table_name} missing columns: {missing}")
        
        return True
    
    @staticmethod
    def check_nulls(df, columns, table_name):
        """Check for NULL values in critical columns"""
        issues = []
        
        for col in columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                issues.append(f"{table_name}.{col}: {null_count} nulls")
        
        return issues
    
    @staticmethod
    def check_date_range(df, date_column, min_date=None, max_date=None):
        """Validate dates are within expected range"""
        issues = []
        
        if min_date:
            too_old = df[df[date_column] < min_date]
            if len(too_old) > 0:
                issues.append(f"{len(too_old)} records before {min_date}")
        
        if max_date:
            too_new = df[df[date_column] > max_date]
            if len(too_new) > 0:
                issues.append(f"{len(too_new)} records after {max_date}")
        
        return issues
    
    @staticmethod
    def check_duplicates(df, columns, table_name):
        """Check for duplicate records"""
        duplicates = df.duplicated(subset=columns, keep=False)
        dup_count = duplicates.sum()
        
        if dup_count > 0:
            return f"{table_name}: {dup_count} duplicate records found"
        
        return None
    
    @staticmethod
    def validate_users(df):
        """Validate users dataframe"""
        print("🔍 Validating users...")
        
        # Check required columns
        required = ['user_id', 'email', 'signup_date']
        DataValidator.check_required_columns(df, required, 'users')
        
        # Check for nulls
        issues = DataValidator.check_nulls(df, ['user_id', 'email'], 'users')
        
        # Check duplicates
        dup_issue = DataValidator.check_duplicates(df, ['user_id'], 'users')
        if dup_issue:
            issues.append(dup_issue)
        
        if issues:
            print(f"   ⚠️  Found {len(issues)} issues")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ✅ Users validation passed")
        
        return issues
    
    @staticmethod
    def validate_subscriptions(df):
        """Validate subscriptions dataframe"""
        print("🔍 Validating subscriptions...")
        
        # Check required columns
        required = ['subscription_id', 'user_id', 'plan_id', 'event_type', 'event_date']
        DataValidator.check_required_columns(df, required, 'subscriptions')
        
        # Check for nulls
        issues = DataValidator.check_nulls(df, required, 'subscriptions')
        
        # Check duplicates
        dup_issue = DataValidator.check_duplicates(df, ['subscription_id'], 'subscriptions')
        if dup_issue:
            issues.append(dup_issue)
        
        # Check valid event types
        valid_events = ['signup', 'upgrade', 'downgrade', 'cancel']
        invalid = df[~df['event_type'].isin(valid_events)]
        if len(invalid) > 0:
            issues.append(f"{len(invalid)} invalid event types")
        
        if issues:
            print(f"   ⚠️  Found {len(issues)} issues")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ✅ Subscriptions validation passed")
        
        return issues