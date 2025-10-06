# MIVA Open University - M&E Dashboard

A professional monitoring and evaluation dashboard for MIVA Open University's AI chatbot system.

## Features

- **Secure Authentication**: Login system with username/password protection
- **Real-time Analytics**: Track feedback, ratings, and user interactions
- **Interactive Visualizations**: Built with Plotly for dynamic charts
- **Data Export**: Download data in CSV format
- **Responsive Design**: Professional UI with MIVA brand colors

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/miva-me-dashboard.git
cd miva-me-dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

Update the database configuration in `app.py` if needed:

```python
DB_CONFIG = {
    "host": "your_host",
    "port": 5432,
    "user": "your_user",
    "password": "your_password",
    "database": "your_database"
}
```

### 4. Run Locally

```bash
streamlit run app.py
```

## Deployment to Streamlit Cloud

### Step 1: Push to GitHub

Ensure all files are committed and pushed to your GitHub repository.

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `yourusername/miva-me-dashboard`
5. Set main file path: `app.py`
6. Click "Deploy"

### Step 3: Configure Secrets

In Streamlit Cloud, go to App settings > Secrets and add:

```toml
[database]
host = "16.170.143.253"
port = 5432
user = "admin"
password = "password123"
database = "miva_ai_db"
```

## Default Login Credentials

- **Username**: `miva_admin`
- **Password**: `password`

⚠️ **Important**: Change these credentials in production!

## Project Structure

```
miva-me-dashboard/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore file
└── .streamlit/
    └── config.toml      # Streamlit configuration
```

## Brand Colors

- **MIVA Red**: #DC143C
- **MIVA Blue**: #1E3A8A
- **MIVA Ash**: #9CA3AF

## Database Tables

The dashboard connects to the following tables:

- `chat_feedback`: User feedback and ratings
- `chat_sessions`: Chat session data
- `chat_messages`: Individual chat messages
- `otp_verifications`: OTP verification records
- `user_feedback`: User feedback records

## Support

For issues or questions, please contact the MIVA technical team.

## License

© 2025 MIVA Open University. All rights reserved.
