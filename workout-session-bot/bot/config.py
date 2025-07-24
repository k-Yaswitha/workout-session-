"""
Configuration settings for the Workout Session Reservation Bot
"""
import os
from datetime import time

# Bot Configuration
BOT_NAME = "WorkoutSessionBot"
VERSION = "1.0.0"

# Target Website Settings
TARGET_URL = os.getenv('GYM_WEBSITE_URL', 'http://localhost:5000')  # Demo website by default
LOGIN_URL = f"{TARGET_URL}/login"
BOOKING_URL = f"{TARGET_URL}/book"

# User Credentials (Use environment variables in production)
USERNAME = os.getenv('GYM_USERNAME', 'demo_user')
PASSWORD = os.getenv('GYM_PASSWORD', 'demo_password')

# Preferred Booking Settings
PREFERRED_TIME_SLOTS = [
    "07:00 AM",  # First choice
    "08:00 AM",  # Second choice
    "09:00 AM"   # Third choice
]

PREFERRED_DAYS_AHEAD = 7  # Book 7 days in advance (typical gym booking window)
PREFERRED_DURATION = "60 minutes"

# Selenium Configuration
HEADLESS_MODE = True  # Set to False for debugging
WAIT_TIMEOUT = 10  # Seconds to wait for elements
PAGE_LOAD_TIMEOUT = 30  # Seconds to wait for page loads

# Chrome Driver Options
CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-logging',
    '--disable-web-security',
    '--allow-running-insecure-content',
    '--window-size=1920,1080'
]

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # Seconds between retries
BACKOFF_MULTIPLIER = 2  # Exponential backoff

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "logs/bot_logs.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Email Notifications (Optional)
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')

# Success/Failure notification settings
SEND_SUCCESS_NOTIFICATIONS = True
SEND_FAILURE_NOTIFICATIONS = True

# Schedule Configuration
BOOKING_TIME = time(6, 0)  # 6:00 AM
TIMEZONE = "America/New_York"  # Adjust based on gym location

# Browser User Agent (for stealth)
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Development/Debug Settings
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
SCREENSHOT_ON_ERROR = True
SCREENSHOT_DIR = "logs/screenshots"

# Cloud Configuration
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'workout-bot-project')
GCP_ZONE = os.getenv('GCP_ZONE', 'us-central1-a')
VM_INSTANCE_NAME = os.getenv('VM_INSTANCE_NAME', 'workout-bot-vm')