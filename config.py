"""
Configuration - loads environment variables
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Database and ETL configuration"""
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'saas_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Data paths
    DATA_PATH = 'data/sample'
    
    @property
    def db_connection_string(self):
        """Get PostgreSQL connection string"""
        return f"host={self.DB_HOST} port={self.DB_PORT} dbname={self.DB_NAME} user={self.DB_USER} password={self.DB_PASSWORD}"


# Create config instance
config = Config()