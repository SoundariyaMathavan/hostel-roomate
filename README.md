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