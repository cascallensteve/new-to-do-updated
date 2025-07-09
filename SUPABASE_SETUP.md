# 🗄️ Supabase Database Setup Guide

## 📋 Current Status
Your Todo App is currently configured to use **SQLite** as a fallback database, so it's working normally. When you're ready to use Supabase, follow this guide.

## 🔍 Issue with Provided Credentials
The hostname `db.wsyhgstkjfwsbnzfcpaw.supabase.co` cannot be resolved, which means:
- ❌ The hostname might be incorrect
- ❌ The Supabase project might not exist
- ❌ Network/DNS issues

## 🚀 How to Get Correct Supabase Credentials

### Step 1: Access Your Supabase Dashboard
1. Go to [https://supabase.com](https://supabase.com)
2. Sign in to your account
3. Select your project

### Step 2: Get Database Connection Details
1. In your Supabase dashboard, go to **Settings** → **Database**
2. Scroll down to **Connection Info**
3. You'll find:
   ```
   Host: your-project-ref.supabase.co
   Database name: postgres
   Port: 5432
   User: postgres
   Password: [your-password]
   ```

### Step 3: Configuration Options

#### Option A: Use Environment Variables (Recommended)
Create a `.env` file in your project root:
```env
# Supabase Database Configuration
SUPABASE_DB_HOST=your-project-ref.supabase.co
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-actual-password
SUPABASE_DB_PORT=5432
```

#### Option B: Use DATABASE_URL
```env
DATABASE_URL=postgresql://postgres:your-password@your-project-ref.supabase.co:5432/postgres
```

## 🛠️ Setup Methods

### Method 1: Automated Setup (Recommended)
Run the setup helper script:
```bash
python setup_supabase.py
```

### Method 2: Manual Setup
1. Create `.env` file with your Supabase credentials
2. Test connection:
   ```bash
   python test_supabase.py
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```

## ✅ Verification Steps

### 1. Test Database Connection
```bash
python test_supabase.py
```

### 2. Check Django Settings
```bash
python manage.py check
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

## 🔧 Troubleshooting

### Common Issues:

#### 1. **"Name or service not known"**
- ✅ Verify the hostname in Supabase dashboard
- ✅ Check internet connection
- ✅ Try using the full DATABASE_URL

#### 2. **"Connection timeout"**
- ✅ Check firewall settings
- ✅ Verify Supabase project is active
- ✅ Ensure IP whitelisting (if enabled)

#### 3. **"Authentication failed"**
- ✅ Double-check password
- ✅ Verify username is correct
- ✅ Check if user has proper permissions

#### 4. **"SSL required"**
- ✅ Ensure `sslmode=require` is set
- ✅ Update psycopg2 if needed

### Network Verification:
```bash
# Test if hostname resolves
nslookup your-project-ref.supabase.co

# Test if port is reachable (Windows)
telnet your-project-ref.supabase.co 5432
```

## 📚 Supabase Dashboard Locations

| Setting | Location in Dashboard |
|---------|----------------------|
| Connection Info | Settings → Database |
| IP Restrictions | Settings → Database → Network Restrictions |
| API Keys | Settings → API |
| Project Settings | Settings → General |

## 🔄 Migration Process

Once Supabase is working:

1. **Backup current data** (if any):
   ```bash
   python manage.py dumpdata > backup.json
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Load data** (if you have backup):
   ```bash
   python manage.py loaddata backup.json
   ```

## 🎯 Production Deployment

For production, use environment variables:
```env
DATABASE_URL=postgresql://postgres:password@host:5432/postgres
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-production-secret-key
```

## 📞 Need Help?

If you continue having issues:

1. **Check Supabase Status**: [https://status.supabase.com](https://status.supabase.com)
2. **Verify Project**: Ensure your Supabase project is active
3. **Contact Support**: Supabase has excellent community support
4. **Alternative**: Consider using Heroku Postgres or Railway for database hosting

## ✨ Current Application Status

Your Todo App is fully functional with:
- ✅ SQLite database (current)
- ✅ User authentication
- ✅ Task management
- ✅ Categories
- ✅ Enhanced dashboard
- ✅ Alert system
- ✅ Email password reset
- ✅ Notes with export

**Ready to switch to Supabase when you get the correct credentials!** 🚀
