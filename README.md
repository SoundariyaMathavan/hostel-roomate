# HostelRoomateFinder

A Django-based hostel management system with roommate finder functionality.

## Quick Start

To run the project immediately:

```bash
cd python/hostel_management
.\venv\bin\python.exe manage.py runserver
```

Then visit: http://127.0.0.1:8000/

## Setup Instructions

1. Navigate to the project directory:
   ```bash
   cd python/hostel_management
   ```

2. Run database migrations:
   ```bash
   .\venv\bin\python.exe manage.py migrate
   ```

3. Start the development server:
   ```bash
   .\venv\bin\python.exe manage.py runserver
   ```

4. Access the application:
   - Main Application: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Admin Credentials

**Username:** `sound`  
**Email:** `sound@gmail.com`  
**Password:** (qwert1234@#A)

## Features

- User registration and authentication
- Room booking system
- Roommate finder functionality
- Payment processing (Stripe integration)
- Admin dashboard for management
- Notification system
- PDF receipt generation

## Deployment Options

### Option 1: Heroku (Recommended for beginners)

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create a new Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set DEBUG=False
   heroku config:set SECRET_KEY=your-secret-key-here
   ```

4. **Deploy**:
   ```bash
   git push heroku master
   ```

5. **Run migrations**:
   ```bash
   heroku run python python/hostel_management/manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   heroku run python python/hostel_management/manage.py createsuperuser
   ```

### Option 2: Railway

1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will automatically detect Django and deploy
4. Add environment variables in Railway dashboard

### Option 3: Render

1. Go to [Render.com](https://render.com)
2. Connect your GitHub repository
3. Choose "Web Service"
4. Set build command: `cd python/hostel_management && pip install -r requirements.txt`
5. Set start command: `cd python/hostel_management && gunicorn hostel_management.wsgi:application`
6. Deploy!

## Environment Variables for Production

Set these environment variables in your deployment platform:

- `DEBUG=False`
- `SECRET_KEY=your-secret-key-here`
- `DATABASE_URL=your-database-url` (automatically set by most platforms)