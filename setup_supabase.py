#!/usr/bin/env python3
"""
Supabase Setup Helper
This script helps you configure and test your Supabase database connection.
"""

import os
import sys

def create_env_file():
    """Create .env file with Supabase configuration"""
    print("Setting up Supabase configuration...")
    print("=" * 50)
    
    # Get Supabase details from user
    print("Please provide your Supabase database details:")
    print("(You can find these in: Supabase Dashboard > Settings > Database)")
    print()
    
    host = input("Database Host (e.g., xyz.supabase.co): ").strip()
    if not host:
        print("ERROR: Host is required!")
        return False
    
    password = input("Database Password: ").strip()
    if not password:
        print("ERROR: Password is required!")
        return False
    
    # Optional fields with defaults
    database = input("Database Name [postgres]: ").strip() or "postgres"
    user = input("Database User [postgres]: ").strip() or "postgres"
    port = input("Database Port [5432]: ").strip() or "5432"
    
    # Create .env content
    env_content = f"""# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True

# Email Configuration
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Supabase Database Configuration
SUPABASE_DB_HOST={host}
SUPABASE_DB_NAME={database}
SUPABASE_DB_USER={user}
SUPABASE_DB_PASSWORD={password}
SUPABASE_DB_PORT={port}

# Alternative DATABASE_URL format
DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{database}
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print()
        print("SUCCESS: .env file created!")
        print("Configuration saved to .env file")
        return True
        
    except Exception as e:
        print(f"ERROR: Could not create .env file - {e}")
        return False

def test_connection():
    """Test the Supabase connection"""
    print()
    print("Testing Supabase connection...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=os.getenv('SUPABASE_DB_HOST'),
            database=os.getenv('SUPABASE_DB_NAME'),
            user=os.getenv('SUPABASE_DB_USER'),
            password=os.getenv('SUPABASE_DB_PASSWORD'),
            port=os.getenv('SUPABASE_DB_PORT'),
            sslmode='require',
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        
        print("SUCCESS: Connected to Supabase!")
        print(f"Database: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"FAILED: Connection error - {e}")
        return False

def run_migrations():
    """Run Django migrations"""
    print()
    print("Running Django migrations...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: Migrations completed!")
            print(result.stdout)
            return True
        else:
            print("FAILED: Migration error")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERROR: Could not run migrations - {e}")
        return False

def main():
    """Main setup process"""
    print("SUPABASE SETUP HELPER")
    print("=" * 50)
    print()
    print("This script will help you:")
    print("1. Configure your Supabase database connection")
    print("2. Test the connection")
    print("3. Run Django migrations")
    print()
    
    # Step 1: Create .env file
    if not create_env_file():
        return False
    
    # Step 2: Test connection
    if not test_connection():
        print()
        print("Connection failed. Please check your Supabase settings:")
        print("1. Verify the database host URL")
        print("2. Check your database password")
        print("3. Ensure your IP is whitelisted in Supabase")
        return False
    
    # Step 3: Run migrations
    if not run_migrations():
        print("Migrations failed. You may need to run them manually:")
        print("python manage.py migrate")
        return False
    
    print()
    print("=" * 50)
    print("SETUP COMPLETE!")
    print("=" * 50)
    print("Your Todo App is now configured to use Supabase!")
    print("You can start the development server with:")
    print("python manage.py runserver")
    
    return True

if __name__ == "__main__":
    main()
