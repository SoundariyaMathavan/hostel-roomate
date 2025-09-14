# 🔍 Debugging 500 Server Error on Render

## Common Causes of 500 Error:

### 1. **Missing Environment Variables**
Check if these are set in Render dashboard:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-app-name.onrender.com
```

### 2. **Database Issues**
- Migrations not run
- Database not accessible

### 3. **Static Files Issues**
- WhiteNoise configuration problems

## 🛠️ **Step-by-Step Debugging:**

### Step 1: Check Render Logs
1. Go to your Render service dashboard
2. Click "Logs" tab
3. Look for error messages (usually in red)
4. Copy the full error traceback

### Step 2: Check Environment Variables
In Render dashboard, verify these are set:
```
DEBUG=False
SECRET_KEY=django-insecure-render-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890
ALLOWED_HOSTS=your-app-name.onrender.com
```

### Step 3: Run Database Migrations
1. Go to "Shell" tab in Render
2. Run: `cd python/hostel_management && python manage.py migrate`

### Step 4: Check Django Settings
The app might be looking for missing settings. Let me create a production-ready settings file.

## 🔧 **Quick Fixes to Try:**

### Fix 1: Add Missing Environment Variables
Add these in Render dashboard:
```
DEBUG=False
SECRET_KEY=django-insecure-render-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Fix 2: Run Migrations
In Shell tab:
```bash
cd python/hostel_management
python manage.py migrate
python manage.py collectstatic --noinput
```

### Fix 3: Create Admin User
```bash
cd python/hostel_management
python manage.py createsuperuser
```

## 📋 **Debug Checklist:**
- [ ] Environment variables set correctly
- [ ] Database migrations completed
- [ ] Static files collected
- [ ] Admin user created
- [ ] Logs checked for specific errors

## 🚨 **Most Likely Issue:**
The 500 error is probably due to missing `SECRET_KEY` environment variable.

**Add this in Render dashboard:**
```
SECRET_KEY=django-insecure-render-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890
```

## 📞 **Need Help?**
Share the error logs from Render dashboard and I'll help you fix the specific issue!
