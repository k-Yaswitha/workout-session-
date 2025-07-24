"""
Utility functions for the Workout Session Reservation Bot
"""
import os
import logging
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Optional, List
import time
import random

from config import *


def setup_logging() -> logging.Logger:
    """Setup logging configuration with rotating file handler."""
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(BOT_NAME)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=LOG_MAX_BYTES, 
        backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    
    # Create console handler for debugging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def send_notification(subject: str, message: str, is_success: bool = True) -> bool:
    """Send email notification about bot execution."""
    if not NOTIFICATION_EMAIL or not EMAIL_USER or not EMAIL_PASSWORD:
        return False
    
    if is_success and not SEND_SUCCESS_NOTIFICATIONS:
        return False
    if not is_success and not SEND_FAILURE_NOTIFICATIONS:
        return False
    
    try:
        # Create message
        msg = MimeMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = NOTIFICATION_EMAIL
        msg['Subject'] = f"[{BOT_NAME}] {subject}"
        
        # Add timestamp and bot info to message
        full_message = f"""
        Bot: {BOT_NAME} v{VERSION}
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Status: {'SUCCESS' if is_success else 'FAILURE'}
        
        {message}
        
        ---
        This is an automated message from your Workout Session Reservation Bot.
        """
        
        msg.attach(MimeText(full_message, 'plain'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, NOTIFICATION_EMAIL, text)
        server.quit()
        
        return True
    except Exception as e:
        # Log error but don't fail the main process
        logger = logging.getLogger(BOT_NAME)
        logger.error(f"Failed to send notification: {str(e)}")
        return False


def get_target_date(days_ahead: int = PREFERRED_DAYS_AHEAD) -> datetime:
    """Get the target date for booking (usually 7 days ahead)."""
    return datetime.now() + timedelta(days=days_ahead)


def format_date_for_booking(date: datetime) -> str:
    """Format date in the format expected by the booking website."""
    return date.strftime('%Y-%m-%d')


def get_current_timestamp() -> str:
    """Get current timestamp as string."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """Add random delay to mimic human behavior."""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def retry_on_failure(max_retries: int = MAX_RETRIES, delay: int = RETRY_DELAY):
    """Decorator for retrying functions on failure with exponential backoff."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (BACKOFF_MULTIPLIER ** attempt)
                        logger = logging.getLogger(BOT_NAME)
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger = logging.getLogger(BOT_NAME)
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {str(e)}")
            
            # If all retries failed, raise the last exception
            raise last_exception
        return wrapper
    return decorator


def validate_time_slot(time_slot: str) -> bool:
    """Validate if time slot is in correct format."""
    try:
        datetime.strptime(time_slot, '%I:%M %p')
        return True
    except ValueError:
        return False


def save_screenshot(driver, filename: str) -> str:
    """Save screenshot for debugging purposes."""
    try:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{timestamp}_{filename}.png")
        driver.save_screenshot(screenshot_path)
        return screenshot_path
    except Exception as e:
        logger = logging.getLogger(BOT_NAME)
        logger.error(f"Failed to save screenshot: {str(e)}")
        return ""


def check_business_hours() -> bool:
    """Check if current time is within business hours for booking."""
    current_hour = datetime.now().hour
    # Most gyms allow booking between 6 AM and 11 PM
    return 6 <= current_hour <= 23


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def is_weekend() -> bool:
    """Check if today is weekend."""
    return datetime.now().weekday() >= 5  # Saturday = 5, Sunday = 6


def get_booking_success_message(time_slot: str, date: str) -> str:
    """Generate success message for booking."""
    return f"""
    ✅ BOOKING SUCCESSFUL!
    
    Time Slot: {time_slot}
    Date: {date}
    Duration: {PREFERRED_DURATION}
    
    Your workout session has been successfully reserved!
    """


def get_booking_failure_message(error: str) -> str:
    """Generate failure message for booking."""
    return f"""
    ❌ BOOKING FAILED!
    
    Error: {error}
    
    The bot will retry during the next scheduled run.
    Please check the logs for more details.
    """


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.logger = logging.getLogger(BOT_NAME)
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting {self.operation_name}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            self.logger.info(f"Completed {self.operation_name} in {duration:.2f} seconds")
        else:
            self.logger.error(f"Failed {self.operation_name} after {duration:.2f} seconds")


def validate_configuration() -> List[str]:
    """Validate bot configuration and return list of issues."""
    issues = []
    
    if not TARGET_URL:
        issues.append("TARGET_URL is not configured")
    
    if not USERNAME or not PASSWORD:
        issues.append("Username or password not configured")
    
    if not PREFERRED_TIME_SLOTS:
        issues.append("No preferred time slots configured")
    
    for time_slot in PREFERRED_TIME_SLOTS:
        if not validate_time_slot(time_slot):
            issues.append(f"Invalid time slot format: {time_slot}")
    
    if PREFERRED_DAYS_AHEAD < 1 or PREFERRED_DAYS_AHEAD > 30:
        issues.append("PREFERRED_DAYS_AHEAD should be between 1 and 30")
    
    return issues