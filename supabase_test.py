#!/usr/bin/env python3
"""
Supabase Database Connection Test
This script helps verify your Supabase database connection details.
"""

import psycopg2
import sys
from urllib.parse import urlparse

def test_connection(host, database, user, password, port='5432'):
    """Test database connection with provided credentials"""
    try:
        print(f"🔄 Testing connection to {host}...")
        
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
            sslmode='require',
            connect_timeout=10
        )
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        
        print(f"✅ Successfully connected to Supabase!")
        print(f"📊 Database version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def parse_database_url(url):
    """Parse DATABASE_URL format"""
    try:
        parsed = urlparse(url)
        return {
            'host': parsed.hostname,
            'database': parsed.path[1:],  # Remove leading slash
            'user': parsed.username,
            'password': parsed.password,
            'port': parsed.port or 5432
        }
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        return None

def main():
    print("🔍 Supabase Database Connection Test")
    print("=" * 40)
    
    # Test with individual components
    print("\n1️⃣ Testing with individual credentials:")
    success = test_connection(
        host='db.wsyhgstkjfwsbnzfcpaw.supabase.co',
        database='postgres',
        user='postgres',
        password='Stevoh@Stevoh2020',
        port='5432'
    )
    
    if not success:
        print("\n💡 Troubleshooting Tips:")
        print("1. Check your Supabase project settings")
        print("2. Verify the database hostname is correct")
        print("3. Ensure your IP is allowed (if IP restrictions are enabled)")
        print("4. Check if your internet connection can reach Supabase")
        print("5. Try using the DATABASE_URL format instead")
        
        print("\n📝 Expected DATABASE_URL format:")
        print("postgresql://postgres:password@host:5432/postgres")
        
        # Try with a constructed DATABASE_URL
        database_url = "postgresql://postgres:Stevoh@Stevoh2020@db.wsyhgstkjfwsbnzfcpaw.supabase.co:5432/postgres"
        print(f"\n2️⃣ Testing with DATABASE_URL format:")
        print(f"URL: {database_url}")
        
        parsed = parse_database_url(database_url)
        if parsed:
            test_connection(**parsed)

if __name__ == "__main__":
    main()
