# HealthSync — Full-Stack Healthcare Web Application

A modern, secure healthcare management platform built with Python Flask, SQLite, and vanilla HTML/CSS/JS.

## Features
- **User Authentication** — Secure signup/login with hashed passwords
- **Dashboard** — Health summary, stats, upcoming appointments, notifications
- **Appointment Management** — Schedule, reschedule, cancel, and track appointments
- **Medication Reminders** — Add medicines with reminders, pause/resume, real-time checks
- **Health Records** — Upload and categorize medical documents
- **User Profile** — Personal info, health details, emergency contact, password change

## Project Structure
```
healthsync/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── healthsync.db           # SQLite database (auto-created)
├── templates/
│   ├── base.html           # Shared layout with sidebar navigation
│   ├── landing.html        # Public landing page
│   ├── login.html          # Login page
│   ├── signup.html         # Registration page
│   ├── dashboard.html      # User dashboard
│   ├── appointments.html   # Appointments management
│   ├── medications.html    # Medication tracker & reminders
│   ├── records.html        # Health records storage
│   └── profile.html        # User profile & settings
└── static/
    └── uploads/            # Uploaded health documents
```

## Setup & Run

### 1. Install Python (3.8+) and pip

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

## First Time Use
1. Go to `http://localhost:5000`
2. Click **Get Started** to create a free account
3. Fill in your name, email, and password
4. You'll be redirected to your dashboard

## Technology Stack
- **Backend**: Python Flask
- **Database**: SQLite (via Python's built-in sqlite3)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Fonts**: Sora + DM Sans (Google Fonts)
- **Icons**: Font Awesome 6
- **Password Security**: Werkzeug PBKDF2 hashing

## API Endpoints
- `GET /api/reminders/check` — Check if any medication is due right now
- `GET /api/upcoming-reminders` — Get next upcoming medication reminders
- `POST /api/notifications/mark-read` — Mark all notifications as read

## Notes
- The medication reminder system checks every 60 seconds automatically
- Files up to 16MB supported (PDF, JPG, PNG, DOC, DOCX)
- All passwords are hashed using PBKDF2-SHA256
- Session-based authentication with Flask sessions
