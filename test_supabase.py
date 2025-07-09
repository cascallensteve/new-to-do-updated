#!/usr/bin/env python3
"""
Simple Supabase Database Connection Test
"""

import psycopg2
import sys

def test_connection():
    """Test database connection with Supabase credentials"""
    print("Testing Supabase connection...")
    
    try:
        # Connection parameters
        conn_params = {
            'host': 'db.wsyhgstkjfwsbnzfcpaw.supabase.co',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'Stevoh@Stevoh2020',
            'port': '5432',
            'sslmode': 'require',
            'connect_timeout': 15
        }
        
        print(f"Connecting to: {conn_params['host']}:{conn_params['port']}")
        
        conn = psycopg2.connect(**conn_params)
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        
        print("SUCCESS: Connected to Supabase!")
        print(f"Database version: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"FAILED: Connection error - {e}")
        if "Name or service not known" in str(e):
            print("ERROR: Cannot resolve hostname. Please check:")
            print("1. Verify the hostname in your Supabase dashboard")
            print("2. Check your internet connection")
            print("3. Ensure DNS is working properly")
        elif "timeout" in str(e):
            print("ERROR: Connection timeout. Please check:")
            print("1. Firewall settings")
            print("2. Network connectivity")
            print("3. Supabase project status")
        return False
        
    except Exception as e:
        print(f"FAILED: Unexpected error - {e}")
        return False

def check_requirements():
    """Check if required packages are installed"""
    try:
        import psycopg2
        print(f"psycopg2 version: {psycopg2.__version__}")
        return True
    except ImportError:
        print("ERROR: psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SUPABASE DATABASE CONNECTION TEST")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    success = test_connection()
    
    if not success:
        print("\nTROUBLESHOoting:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to Settings > Database")
        print("3. Check the connection details:")
        print("   - Host")
        print("   - Database name")
        print("   - Port")
        print("   - Password")
        print("4. Ensure connection pooling is enabled")
        print("5. Check if your IP needs to be whitelisted")
    
    print("=" * 50)
