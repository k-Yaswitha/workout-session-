#!/bin/bash

# Workout Session Reservation Bot - Complete Demo Runner
# This script sets up and runs the complete demonstration

set -e

echo "🏋️ Workout Session Reservation Bot - Complete Demo"
echo "=================================================="
echo "This demo will:"
echo "1. Set up the Python environment"
echo "2. Install dependencies"
echo "3. Start the demo website"
echo "4. Run the bot in demo mode"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.9+ and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "bot" ] || [ ! -d "demo_website" ]; then
    echo "❌ Please run this script from the project root directory"
    echo "Expected structure:"
    echo "  - README.md"
    echo "  - bot/"
    echo "  - demo_website/"
    exit 1
fi

echo "✅ Project structure verified"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install bot dependencies
echo "📦 Installing bot dependencies..."
cd bot
pip install -r requirements.txt
cd ..

# Install website dependencies
echo "📦 Installing website dependencies..."
cd demo_website
pip install -r requirements.txt
cd ..

# Create logs directory
mkdir -p logs

echo ""
echo "🎯 Setup complete! Choose a demo mode:"
echo ""
echo "1. 🌐 Website Only - Start the demo website"
echo "2. 🤖 Bot Test - Test bot configuration"
echo "3. 🔄 Full Demo - Website + Bot automation"
echo "4. 🔧 Manual Setup - Instructions for manual testing"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🌐 Starting Demo Website..."
        echo "Visit http://localhost:5000 in your browser"
        echo "Login with: username=demo_user, password=demo_password"
        echo ""
        echo "Press Ctrl+C to stop the website"
        cd demo_website
        python3 app.py
        ;;
    
    2)
        echo ""
        echo "🤖 Testing Bot Configuration..."
        cd bot
        python3 test_bot.py --mode config
        echo ""
        echo "Want to run a dry-run test? (y/n)"
        read -p "> " dry_run
        if [ "$dry_run" = "y" ] || [ "$dry_run" = "Y" ]; then
            python3 test_bot.py --mode dry-run
        fi
        ;;
    
    3)
        echo ""
        echo "🔄 Starting Full Demo..."
        echo "This will start the website and then run the bot"
        echo ""
        
        # Start website in background
        echo "🌐 Starting demo website in background..."
        cd demo_website
        python3 app.py &
        WEBSITE_PID=$!
        cd ..
        
        # Wait for website to start
        echo "⏳ Waiting for website to start..."
        sleep 3
        
        # Check if website is running
        if curl -s http://localhost:5000 > /dev/null; then
            echo "✅ Website is running at http://localhost:5000"
        else
            echo "❌ Website failed to start"
            kill $WEBSITE_PID 2>/dev/null || true
            exit 1
        fi
        
        # Run bot test
        echo ""
        echo "🤖 Running bot automation..."
        cd bot
        python3 test_bot.py --mode full
        
        # Stop website
        echo ""
        echo "🛑 Stopping demo website..."
        kill $WEBSITE_PID 2>/dev/null || true
        
        echo "✅ Full demo completed!"
        ;;
    
    4)
        echo ""
        echo "🔧 Manual Setup Instructions"
        echo "==========================="
        echo ""
        echo "1. Start the demo website:"
        echo "   cd demo_website"
        echo "   python3 app.py"
        echo "   # Visit http://localhost:5000"
        echo ""
        echo "2. In another terminal, test the bot:"
        echo "   cd bot"
        echo "   python3 test_bot.py --mode config    # Test configuration"
        echo "   python3 test_bot.py --mode dry-run   # Test without website"
        echo "   python3 test_bot.py --mode full      # Full automation test"
        echo ""
        echo "3. Run the bot manually:"
        echo "   cd bot"
        echo "   python3 reservation_bot.py"
        echo ""
        echo "4. For production deployment:"
        echo "   # See deployment/setup_vm.sh for GCP deployment"
        echo ""
        ;;
    
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Demo session completed!"
echo ""
echo "📋 What you've seen:"
echo "• Modern Flask-based gym booking website"
echo "• Selenium-powered automation bot"
echo "• Comprehensive error handling and logging"
echo "• Cloud deployment ready architecture"
echo ""
echo "📚 For interview discussions:"
echo "• Code walkthrough: Check bot/reservation_bot.py"
echo "• Architecture: See README.md"
echo "• Deployment: Review deployment/setup_vm.sh"
echo "• Testing: Explore bot/test_bot.py"
echo ""
echo "Thank you for trying the Workout Session Reservation Bot demo!"