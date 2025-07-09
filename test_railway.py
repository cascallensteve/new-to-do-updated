#!/usr/bin/env python3
"""
Railway Database Connection Test
"""

import psycopg2
import sys

def test_railway_connection():
    """Test database connection with Railway credentials"""
    print("Testing Railway PostgreSQL connection...")
    
    try:
        # Railway connection parameters
        conn_params = {
            'host': 'metro.proxy.rlwy.net',
            'database': 'railway',
            'user': 'postgres',
            'password': 'QWcNAKCHWnEhpldwjcEWZdWZtHYOFzBX',
            'port': '52529',
            'sslmode': 'require',
            'connect_timeout': 15
        }
        
        print(f"Connecting to: {conn_params['host']}:{conn_params['port']}")
        print(f"Database: {conn_params['database']}")
        
        conn = psycopg2.connect(**conn_params)
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        
        print("SUCCESS: Connected to Railway PostgreSQL!")
        print(f"Database version: {version[0][:80]}...")
        
        # Test database info
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"Current database: {db_info[0]}")
        print(f"Current user: {db_info[1]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"FAILED: Connection error - {e}")
        if "Name or service not known" in str(e):
            print("ERROR: Cannot resolve hostname.")
        elif "timeout" in str(e):
            print("ERROR: Connection timeout.")
        elif "authentication failed" in str(e):
            print("ERROR: Invalid credentials.")
        return False
        
    except Exception as e:
        print(f"FAILED: Unexpected error - {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("RAILWAY DATABASE CONNECTION TEST")
    print("=" * 60)
    
    success = test_railway_connection()
    
    if success:
        print("\n✅ Railway connection is working!")
        print("You can now run Django migrations.")
    else:
        print("\n❌ Railway connection failed.")
        print("Please check your Railway database credentials.")
    
    print("=" * 60)
