#!/bin/bash

# Workout Session Reservation Bot - GCP VM Setup Script
# This script sets up a Google Cloud VM for running the bot

set -e  # Exit on any error

echo "🏋️ Setting up Workout Session Reservation Bot on Google Cloud VM..."
echo "=================================================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python 3.9+ and pip
echo "🐍 Installing Python and dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv git wget unzip

# Install Google Chrome
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update -y
sudo apt-get install -y google-chrome-stable

# Install ChromeDriver
echo "🚗 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
echo "Chrome version: $CHROME_VERSION, ChromeDriver version: $CHROMEDRIVER_VERSION"

wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Verify installations
echo "✅ Verifying installations..."
python3 --version
google-chrome --version
chromedriver --version

# Create bot user and directories
echo "👤 Setting up bot user and directories..."
sudo useradd -m -s /bin/bash workoutbot || echo "User workoutbot already exists"
sudo mkdir -p /opt/workout-bot
sudo chown workoutbot:workoutbot /opt/workout-bot

# Clone or copy bot code (assuming it's already uploaded)
echo "📁 Setting up bot directory structure..."
sudo -u workoutbot mkdir -p /opt/workout-bot/{bot,logs,logs/screenshots}

# Create Python virtual environment
echo "🔧 Creating Python virtual environment..."
sudo -u workoutbot python3 -m venv /opt/workout-bot/venv
sudo -u workoutbot /opt/workout-bot/venv/bin/pip install --upgrade pip

# Copy bot files (this assumes files are in the current directory)
if [ -d "bot" ]; then
    echo "📋 Copying bot files..."
    sudo cp -r bot/* /opt/workout-bot/bot/
    sudo chown -R workoutbot:workoutbot /opt/workout-bot/bot/
fi

# Install Python dependencies
if [ -f "/opt/workout-bot/bot/requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    sudo -u workoutbot /opt/workout-bot/venv/bin/pip install -r /opt/workout-bot/bot/requirements.txt
fi

# Create systemd service for the bot
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/workout-bot.service > /dev/null <<EOF
[Unit]
Description=Workout Session Reservation Bot
After=network.target

[Service]
Type=oneshot
User=workoutbot
WorkingDirectory=/opt/workout-bot/bot
Environment=PATH=/opt/workout-bot/venv/bin
ExecStart=/opt/workout-bot/venv/bin/python reservation_bot.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create systemd timer for daily execution at 6 AM
echo "⏰ Creating systemd timer for daily execution..."
sudo tee /etc/systemd/system/workout-bot.timer > /dev/null <<EOF
[Unit]
Description=Run Workout Bot Daily at 6 AM
Requires=workout-bot.service

[Timer]
OnCalendar=*-*-* 06:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start the timer
echo "▶️ Enabling systemd timer..."
sudo systemctl daemon-reload
sudo systemctl enable workout-bot.timer
sudo systemctl start workout-bot.timer

# Create log rotation configuration
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/workout-bot > /dev/null <<EOF
/opt/workout-bot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 workoutbot workoutbot
}
EOF

# Set up firewall (if needed for demo website)
echo "🔥 Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 5000/tcp  # For demo website
sudo ufw --force enable

# Create environment file template
echo "📄 Creating environment file template..."
sudo -u workoutbot tee /opt/workout-bot/.env.template > /dev/null <<EOF
# Workout Session Reservation Bot - Environment Variables
# Copy this file to .env and fill in your actual values

# Target Website
GYM_WEBSITE_URL=http://localhost:5000
GYM_USERNAME=demo_user
GYM_PASSWORD=demo_password

# Email Notifications (Optional)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
NOTIFICATION_EMAIL=your-notification-email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Google Cloud Configuration
GCP_PROJECT_ID=your-project-id
GCP_ZONE=us-central1-a
VM_INSTANCE_NAME=workout-bot-vm

# Debug Mode
DEBUG_MODE=false
EOF

# Install additional monitoring tools
echo "📊 Installing monitoring tools..."
sudo apt-get install -y htop ncdu tree

# Create helpful scripts
echo "🔧 Creating utility scripts..."

# Status check script
sudo tee /opt/workout-bot/status.sh > /dev/null <<'EOF'
#!/bin/bash
echo "=== Workout Bot Status ==="
echo "Timer Status:"
sudo systemctl status workout-bot.timer --no-pager
echo -e "\nLast 10 log entries:"
sudo journalctl -u workout-bot.service -n 10 --no-pager
echo -e "\nDisk usage:"
df -h /opt/workout-bot
echo -e "\nBot files:"
ls -la /opt/workout-bot/bot/
EOF

# Manual run script
sudo tee /opt/workout-bot/run-bot.sh > /dev/null <<'EOF'
#!/bin/bash
echo "Running Workout Bot manually..."
cd /opt/workout-bot/bot
sudo -u workoutbot /opt/workout-bot/venv/bin/python reservation_bot.py
EOF

# Log viewer script
sudo tee /opt/workout-bot/view-logs.sh > /dev/null <<'EOF'
#!/bin/bash
echo "=== Recent Bot Logs ==="
if [ -f "/opt/workout-bot/logs/bot_logs.log" ]; then
    tail -f /opt/workout-bot/logs/bot_logs.log
else
    echo "No log file found. Showing systemd logs:"
    sudo journalctl -u workout-bot.service -f
fi
EOF

# Make scripts executable
sudo chmod +x /opt/workout-bot/*.sh

# Display status and next steps
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo "✅ Google Chrome and ChromeDriver installed"
echo "✅ Python virtual environment created"
echo "✅ Systemd service and timer configured"
echo "✅ Log rotation configured"
echo "✅ Firewall configured"
echo ""
echo "📋 Next Steps:"
echo "1. Copy your bot code to /opt/workout-bot/bot/"
echo "2. Configure environment variables in /opt/workout-bot/.env"
echo "3. Test the bot: sudo /opt/workout-bot/run-bot.sh"
echo "4. Check status: sudo /opt/workout-bot/status.sh"
echo "5. View logs: sudo /opt/workout-bot/view-logs.sh"
echo ""
echo "⏰ Bot will run automatically every day at 6:00 AM"
echo "🔧 Use 'sudo systemctl status workout-bot.timer' to check timer status"
echo ""
echo "🌐 To run demo website:"
echo "   cd /path/to/demo_website && python3 app.py"

# Show timer status
echo ""
echo "Current timer status:"
sudo systemctl status workout-bot.timer --no-pager