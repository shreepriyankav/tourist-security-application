# tourist-security-application

# Tourist Safety Application

A Flask-based web application for managing tourist safety, including registration, itinerary management, geofencing alerts, and digital ID generation.

## Features

- **Tourist Registration & Login**: Secure user authentication with hashed passwords
- **Digital ID Generation**: Unique digital identification for tourists
- **Itinerary Management**: Create, view, and cancel travel itineraries
- **Geofencing Alerts**: Safety warnings for restricted/emergency zones
- **Check-in System**: Tourist status tracking
- **Admin Dashboard**: Administrative controls and monitoring
- **Email Notifications**: Automated safety alerts

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone or download the project**
   ```bash
   cd "e:\Project\2401_(Priyanka)_Full CODE_20.12"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install required packages**
   ```bash
   pip install flask
   ```

## Configuration

1. **Email Settings**: Update email credentials in `CODE/app.py`:
   ```python
   EMAIL_ADDRESS = "your-email@gmail.com"
   EMAIL_PASSWORD = "your-app-password"
   ADMIN_EMAIL = "admin-email@gmail.com"
   ```

2. **Database**: The SQLite database will be created automatically on first run.

## Running the Application

1. **Navigate to the CODE directory**
   ```bash
   cd CODE
   ```

2. **Run the Flask application**
   ```bash
   python app.py
   ```

3. **Access the application**
   - Open your web browser
   - Go to: `http://localhost:5000`

## Usage

### Admin Access
- URL: `http://localhost:5000/admin`
- Username: `admin`
- Password: `admin123`

### Tourist Features
1. **Register**: Create a new tourist account
2. **Login**: Access your dashboard
3. **Create Itinerary**: Plan your trips
4. **Digital ID**: View your unique digital identification
5. **Geofence Alerts**: Check zone safety status
6. **Check-in**: Update your status

## Project Structure

```
2401_(Priyanka)_Full CODE_20.12/
├── CODE/
│   ├── templates/          # HTML templates
│   ├── app.py             # Main Flask application
│   ├── database.db        # SQLite database
│   └── inspect_db.py      # Database inspection utility
└── README.md              # This file
```

## Database Tables

- **tourists**: User registration data
- **itineraries**: Travel plans and schedules
- **geofences**: Safety zone definitions
- **checkins**: Tourist status updates

## Security Notes

- Passwords are hashed using SHA-256
- Session management for user authentication
- Email alerts for safety notifications

## Troubleshooting

1. **Port already in use**: Change the port in app.py:
   ```python
   app.run(debug=True, port=5001)
   ```

2. **Email not working**: Ensure you're using an app-specific password for Gmail

3. **Database issues**: Delete `database.db` to reset the database

## Development

To run in development mode with auto-reload:
```bash
export FLASK_ENV=development  # Linux/macOS
set FLASK_ENV=development     # Windows
python app.py
```

## Support

For issues or questions, check the code comments or modify the application as needed for your specific requirements.
