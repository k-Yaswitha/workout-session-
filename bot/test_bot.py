#!/usr/bin/env python3
"""
Test Script for Workout Session Reservation Bot

This script allows you to test the bot functionality in different modes:
1. Full automation test (requires running demo website)
2. Configuration validation
3. Dry run mode (no actual booking)

Usage:
    python test_bot.py --mode [full|config|dry-run]
"""

import sys
import argparse
from datetime import datetime, timedelta

# Import bot modules
try:
    from reservation_bot import WorkoutReservationBot
    from utils import setup_logging, validate_configuration, PerformanceTimer
    from config import *
except ImportError as e:
    print(f"❌ Error importing bot modules: {e}")
    print("Make sure you're running this from the bot directory with all required packages installed.")
    sys.exit(1)


def test_configuration():
    """Test and validate bot configuration."""
    print("🔧 Testing Bot Configuration")
    print("=" * 40)
    
    # Test imports
    print("✅ All modules imported successfully")
    
    # Validate configuration
    issues = validate_configuration()
    if issues:
        print("❌ Configuration Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Configuration validation passed")
    
    # Display key settings
    print(f"\n📋 Bot Configuration:")
    print(f"   Bot Name: {BOT_NAME} v{VERSION}")
    print(f"   Target URL: {TARGET_URL}")
    print(f"   Username: {USERNAME}")
    print(f"   Preferred Time Slots: {PREFERRED_TIME_SLOTS}")
    print(f"   Days Ahead: {PREFERRED_DAYS_AHEAD}")
    print(f"   Headless Mode: {HEADLESS_MODE}")
    print(f"   Max Retries: {MAX_RETRIES}")
    
    return True


def test_dry_run():
    """Test bot logic without actual web interaction."""
    print("🏃 Running Dry Run Test")
    print("=" * 40)
    
    # Setup logging
    logger = setup_logging()
    
    try:
        # Test date calculations
        target_date = datetime.now() + timedelta(days=PREFERRED_DAYS_AHEAD)
        print(f"✅ Target booking date: {target_date.strftime('%Y-%m-%d')}")
        
        # Test time slot validation
        for slot in PREFERRED_TIME_SLOTS:
            try:
                datetime.strptime(slot, '%I:%M %p')
                print(f"✅ Time slot '{slot}' is valid")
            except ValueError:
                print(f"❌ Time slot '{slot}' is invalid")
                return False
        
        # Test logging
        logger.info("Test log message")
        print("✅ Logging system working")
        
        # Test email configuration (if configured)
        if EMAIL_USER and EMAIL_PASSWORD:
            print("✅ Email notifications configured")
        else:
            print("ℹ️  Email notifications not configured (optional)")
        
        print("\n🎉 Dry run completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Dry run failed: {str(e)}")
        return False


def test_full_automation():
    """Test full bot automation (requires demo website to be running)."""
    print("🤖 Running Full Automation Test")
    print("=" * 40)
    
    # Check if demo website is accessible
    import requests
    try:
        response = requests.get(TARGET_URL, timeout=5)
        if response.status_code == 200:
            print(f"✅ Demo website is accessible at {TARGET_URL}")
        else:
            print(f"❌ Demo website returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access demo website at {TARGET_URL}")
        print(f"   Error: {str(e)}")
        print("   Make sure the demo website is running:")
        print("   cd demo_website && python app.py")
        return False
    
    # Run the bot
    try:
        with PerformanceTimer("Full Bot Test"):
            bot = WorkoutReservationBot()
            success = bot.run()
            
        if success:
            print("🎉 Bot execution completed successfully!")
            print("✅ Booking was made (or attempted based on availability)")
        else:
            print("⚠️  Bot execution completed but booking failed")
            print("   This could be due to:")
            print("   - No available time slots")
            print("   - All preferred slots already booked")
            print("   - Website interaction issues")
        
        return success
        
    except Exception as e:
        print(f"❌ Bot execution failed: {str(e)}")
        return False


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description='Test Workout Session Reservation Bot')
    parser.add_argument('--mode', 
                       choices=['config', 'dry-run', 'full'], 
                       default='config',
                       help='Test mode to run')
    
    args = parser.parse_args()
    
    print("🏋️ Workout Session Reservation Bot - Test Suite")
    print("=" * 50)
    print(f"Test Mode: {args.mode}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    success = False
    
    if args.mode == 'config':
        success = test_configuration()
        
    elif args.mode == 'dry-run':
        success = test_configuration() and test_dry_run()
        
    elif args.mode == 'full':
        success = test_configuration() and test_full_automation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        print("\n📋 Next Steps:")
        print("1. For demo: Start the website with 'cd demo_website && python app.py'")
        print("2. For production: Configure your actual gym website URL")
        print("3. Deploy to GCP: Use the deployment scripts in deployment/")
        print("4. Monitor: Check logs with the provided monitoring scripts")
    else:
        print("❌ Some tests failed. Please check the configuration and try again.")
    
    print("=" * 50)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()