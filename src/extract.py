"""
Extract module - reads data from CSV and JSON files
Simple and straightforward data extraction
"""

import pandas as pd
import json
from pathlib import Path


class DataExtractor:
    """Handles extraction from various file formats"""
    
    def __init__(self, data_path='data/sample'):
        self.data_path = Path(data_path)
    
    def extract_users(self):
        """Read users from CSV"""
        file_path = self.data_path / 'users.csv'
        print(f"📖 Reading users from {file_path}")
        
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {len(df)} users")
        return df
    
    def extract_subscriptions(self):
        """Read subscriptions from JSON"""
        file_path = self.data_path / 'subscriptions.json'
        print(f"📖 Reading subscriptions from {file_path}")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        print(f"✅ Loaded {len(df)} subscription events")
        return df
    
    def extract_events(self):
        """Read usage events from JSON"""
        file_path = self.data_path / 'events.json'
        print(f"📖 Reading events from {file_path}")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        print(f"✅ Loaded {len(df)} events")
        return df
    
    def extract_all(self):
        """Extract all data sources"""
        print("\n" + "="*50)
        print("EXTRACT PHASE")
        print("="*50)
        
        users = self.extract_users()
        subscriptions = self.extract_subscriptions()
        events = self.extract_events()
        
        print("\n✅ Extraction complete!")
        
        return {
            'users': users,
            'subscriptions': subscriptions,
            'events': events
        }


# Simple test
if __name__ == '__main__':
    extractor = DataExtractor()
    data = extractor.extract_all()
    
    print("\n📊 Data Preview:")
    print("\nUsers:")
    print(data['users'].head())
    print("\nSubscriptions:")
    print(data['subscriptions'].head())