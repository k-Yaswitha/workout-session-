#!/usr/bin/env python3
"""
Workout Session Reservation Bot - Main Script

This bot automatically reserves workout sessions using Selenium WebDriver.
It runs daily at 6 AM to book preferred time slots 7 days in advance.

Author: Workout Session Bot
Version: 1.0.0
"""

import sys
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementClickInterceptedException
)

# Import our modules
from config import *
from utils import (
    setup_logging, send_notification, get_target_date, 
    format_date_for_booking, random_delay, retry_on_failure,
    save_screenshot, PerformanceTimer, validate_configuration,
    get_booking_success_message, get_booking_failure_message
)


class WorkoutReservationBot:
    """Main bot class for automating workout session reservations."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.driver = None
        self.is_logged_in = False
        
        # Validate configuration
        config_issues = validate_configuration()
        if config_issues:
            for issue in config_issues:
                self.logger.error(f"Configuration issue: {issue}")
            raise ValueError("Bot configuration is invalid. Please check your config.py file.")
        
        self.logger.info(f"Initializing {BOT_NAME} v{VERSION}")
    
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with configured options."""
        try:
            chrome_options = Options()
            
            # Add configured Chrome options
            for option in CHROME_OPTIONS:
                chrome_options.add_argument(option)
            
            # Set headless mode
            if HEADLESS_MODE:
                chrome_options.add_argument('--headless')
            
            # Set user agent
            chrome_options.add_argument(f'--user-agent={USER_AGENT}')
            
            # Additional stealth options
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            
            self.logger.info("Chrome WebDriver initialized successfully")
            return self.driver
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome driver: {str(e)}")
            raise
    
    @retry_on_failure()
    def login(self) -> bool:
        """Login to the gym website."""
        try:
            with PerformanceTimer("Login process"):
                self.logger.info(f"Navigating to login page: {LOGIN_URL}")
                self.driver.get(LOGIN_URL)
                
                # Wait for login form to load
                wait = WebDriverWait(self.driver, WAIT_TIMEOUT)
                
                # Find and fill username field
                username_field = wait.until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                username_field.clear()
                username_field.send_keys(USERNAME)
                self.logger.info("Username entered")
                
                random_delay(0.5, 1.5)
                
                # Find and fill password field
                password_field = self.driver.find_element(By.NAME, "password")
                password_field.clear()
                password_field.send_keys(PASSWORD)
                self.logger.info("Password entered")
                
                random_delay(1.0, 2.0)
                
                # Click login button
                login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                login_button.click()
                self.logger.info("Login button clicked")
                
                # Wait for login to complete (check for dashboard or booking page)
                try:
                    wait.until(
                        EC.any_of(
                            EC.url_contains("/dashboard"),
                            EC.url_contains("/book"),
                            EC.presence_of_element_located((By.CLASS_NAME, "welcome-message"))
                        )
                    )
                    self.is_logged_in = True
                    self.logger.info("Login successful")
                    return True
                    
                except TimeoutException:
                    # Check for error messages
                    try:
                        error_element = self.driver.find_element(By.CLASS_NAME, "error-message")
                        error_text = error_element.text
                        self.logger.error(f"Login failed: {error_text}")
                    except NoSuchElementException:
                        self.logger.error("Login failed: Unknown error")
                    
                    if SCREENSHOT_ON_ERROR:
                        save_screenshot(self.driver, "login_failure")
                    
                    return False
                    
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            if SCREENSHOT_ON_ERROR and self.driver:
                save_screenshot(self.driver, "login_error")
            raise
    
    @retry_on_failure()
    def navigate_to_booking_page(self) -> bool:
        """Navigate to the booking page."""
        try:
            self.logger.info(f"Navigating to booking page: {BOOKING_URL}")
            self.driver.get(BOOKING_URL)
            
            wait = WebDriverWait(self.driver, WAIT_TIMEOUT)
            
            # Wait for booking form to load
            wait.until(
                EC.presence_of_element_located((By.ID, "booking-form"))
            )
            
            self.logger.info("Booking page loaded successfully")
            return True
            
        except TimeoutException:
            self.logger.error("Booking page failed to load")
            if SCREENSHOT_ON_ERROR:
                save_screenshot(self.driver, "booking_page_timeout")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to booking page: {str(e)}")
            raise
    
    @retry_on_failure()
    def make_reservation(self) -> bool:
        """Attempt to make a reservation for the preferred time slots."""
        try:
            with PerformanceTimer("Reservation process"):
                target_date = get_target_date()
                formatted_date = format_date_for_booking(target_date)
                
                self.logger.info(f"Attempting to book for date: {formatted_date}")
                
                # Set the date
                date_field = self.driver.find_element(By.ID, "booking-date")
                date_field.clear()
                date_field.send_keys(formatted_date)
                self.logger.info(f"Date set to: {formatted_date}")
                
                random_delay(0.5, 1.0)
                
                # Try each preferred time slot
                for time_slot in PREFERRED_TIME_SLOTS:
                    self.logger.info(f"Attempting to book time slot: {time_slot}")
                    
                    try:
                        # Select time slot
                        time_select = Select(self.driver.find_element(By.ID, "time-slot"))
                        time_select.select_by_visible_text(time_slot)
                        
                        random_delay(0.5, 1.0)
                        
                        # Select duration
                        duration_select = Select(self.driver.find_element(By.ID, "duration"))
                        duration_select.select_by_visible_text(PREFERRED_DURATION)
                        
                        random_delay(0.5, 1.0)
                        
                        # Click book button
                        book_button = self.driver.find_element(By.ID, "book-button")
                        
                        # Check if button is enabled (time slot available)
                        if not book_button.is_enabled():
                            self.logger.warning(f"Time slot {time_slot} is not available")
                            continue
                        
                        book_button.click()
                        self.logger.info(f"Book button clicked for {time_slot}")
                        
                        random_delay(2.0, 3.0)
                        
                        # Check for success message
                        wait = WebDriverWait(self.driver, WAIT_TIMEOUT)
                        try:
                            success_element = wait.until(
                                EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
                            )
                            success_message = success_element.text
                            
                            if "successfully" in success_message.lower() or "confirmed" in success_message.lower():
                                self.logger.info(f"✅ Booking successful for {time_slot} on {formatted_date}")
                                
                                # Send success notification
                                notification_message = get_booking_success_message(time_slot, formatted_date)
                                send_notification("Booking Successful", notification_message, is_success=True)
                                
                                return True
                            else:
                                self.logger.warning(f"Unexpected success message: {success_message}")
                                
                        except TimeoutException:
                            # Check for error message
                            try:
                                error_element = self.driver.find_element(By.CLASS_NAME, "error-message")
                                error_text = error_element.text
                                self.logger.warning(f"Booking failed for {time_slot}: {error_text}")
                                
                                # If time slot is full, try next one
                                if "full" in error_text.lower() or "unavailable" in error_text.lower():
                                    continue
                                else:
                                    # Other error, might be worth retrying
                                    raise Exception(error_text)
                                    
                            except NoSuchElementException:
                                self.logger.warning(f"No clear success/error message for {time_slot}")
                                continue
                    
                    except ElementClickInterceptedException:
                        self.logger.warning(f"Could not click book button for {time_slot} - element intercepted")
                        continue
                    except Exception as e:
                        self.logger.warning(f"Error booking {time_slot}: {str(e)}")
                        continue
                
                # If we get here, all time slots failed
                error_msg = f"All preferred time slots unavailable for {formatted_date}"
                self.logger.error(error_msg)
                
                # Send failure notification
                notification_message = get_booking_failure_message(error_msg)
                send_notification("Booking Failed", notification_message, is_success=False)
                
                if SCREENSHOT_ON_ERROR:
                    save_screenshot(self.driver, "all_slots_unavailable")
                
                return False
                
        except Exception as e:
            error_msg = f"Reservation process failed: {str(e)}"
            self.logger.error(error_msg)
            
            if SCREENSHOT_ON_ERROR and self.driver:
                save_screenshot(self.driver, "reservation_error")
            
            # Send failure notification
            notification_message = get_booking_failure_message(error_msg)
            send_notification("Booking Error", notification_message, is_success=False)
            
            raise
    
    def run(self) -> bool:
        """Main execution method."""
        success = False
        
        try:
            self.logger.info("=" * 50)
            self.logger.info(f"Starting {BOT_NAME} execution")
            self.logger.info(f"Target URL: {TARGET_URL}")
            self.logger.info(f"Preferred time slots: {PREFERRED_TIME_SLOTS}")
            self.logger.info("=" * 50)
            
            # Setup WebDriver
            self.setup_driver()
            
            # Login
            if self.login():
                # Navigate to booking page
                if self.navigate_to_booking_page():
                    # Make reservation
                    success = self.make_reservation()
                else:
                    self.logger.error("Failed to navigate to booking page")
            else:
                self.logger.error("Login failed")
            
        except Exception as e:
            self.logger.error(f"Bot execution failed: {str(e)}")
            
        finally:
            # Cleanup
            if self.driver:
                try:
                    self.driver.quit()
                    self.logger.info("WebDriver closed successfully")
                except Exception as e:
                    self.logger.warning(f"Error closing WebDriver: {str(e)}")
            
            self.logger.info(f"Bot execution completed. Success: {success}")
            self.logger.info("=" * 50)
        
        return success


def main():
    """Main entry point."""
    try:
        bot = WorkoutReservationBot()
        success = bot.run()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nBot execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()