# Workout Session Reservation Bot

## 🏋️ Project Overview

An intelligent automation bot that automatically reserves workout session timeslots using Python, Selenium WebDriver, and Google Cloud Platform. The system runs daily at 6 AM to secure preferred workout times without manual intervention.

## 🎯 Key Features

- **Automated Reservation**: Uses Selenium to interact with gym booking websites
- **Cloud Deployment**: Runs on Google Cloud VM for 24/7 availability
- **Scheduled Execution**: Cron job triggers reservation at optimal booking time (6 AM)
- **Error Handling**: Robust retry logic and notification systems
- **Demo Website**: Includes a sample gym booking site for demonstration
- **Logging & Monitoring**: Comprehensive logging for debugging and analytics

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Cron Scheduler │────│  Python Bot      │────│  Target Website │
│  (6 AM Daily)   │    │  (Selenium)      │    │  (Gym Booking)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Google Cloud VM │
                    │  (Ubuntu Linux)  │
                    └──────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Python 3.9+
- **Automation**: Selenium WebDriver (Chrome)
- **Cloud Platform**: Google Cloud Platform (Compute Engine)
- **Scheduling**: Cron
- **Demo Frontend**: Flask + HTML/CSS/JavaScript
- **Containerization**: Docker (optional)
- **Monitoring**: Python logging + Email notifications

## 📋 Project Structure

```
workout-session-bot/
├── bot/
│   ├── reservation_bot.py      # Main bot logic
│   ├── config.py              # Configuration settings
│   ├── utils.py               # Helper functions
│   └── requirements.txt       # Python dependencies
├── demo_website/
│   ├── app.py                 # Flask demo gym website
│   ├── templates/             # HTML templates
│   ├── static/               # CSS/JS files
│   └── requirements.txt      # Web app dependencies
├── deployment/
│   ├── setup_vm.sh           # GCP VM setup script
│   ├── install_dependencies.sh
│   ├── crontab_config        # Cron job configuration
│   └── Dockerfile           # Docker configuration
├── logs/
│   └── bot_logs.log         # Application logs
└── docs/
    ├── SETUP.md             # Setup instructions
    └── DEMO.md              # Demo instructions
```

## 🚀 Quick Start

### 1. Local Development Setup

```bash
# Clone and setup
git clone <repository>
cd workout-session-bot

# Setup Python environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r bot/requirements.txt

# Install Chrome and ChromeDriver
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install google-chrome-stable
wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/LATEST_RELEASE/chromedriver_linux64.zip
unzip /tmp/chromedriver.zip -d /usr/local/bin/

# Run the demo website
cd demo_website
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000

# Test the bot
cd ../bot
python reservation_bot.py
```

### 2. Google Cloud Deployment

```bash
# Create GCP VM
gcloud compute instances create workout-bot-vm \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-micro \
    --zone=us-central1-a

# Deploy and setup
gcloud compute scp deployment/setup_vm.sh workout-bot-vm:~
gcloud compute ssh workout-bot-vm --command="chmod +x setup_vm.sh && ./setup_vm.sh"
```

## 🎬 For Interviewers

### Demo Scenarios

1. **Live Bot Demonstration**: Shows automated form filling and submission
2. **Code Walkthrough**: Explains Selenium automation patterns
3. **Cloud Architecture**: Discusses GCP deployment and scheduling
4. **Error Handling**: Demonstrates retry logic and edge cases
5. **Scalability**: How to extend for multiple users/gyms

### Key Interview Points

- **Problem Solving**: Automated a repetitive manual task
- **Web Technologies**: DOM manipulation, form handling, session management
- **Cloud Computing**: VM management, scheduled tasks, resource optimization
- **System Design**: Modular architecture, configuration management
- **DevOps**: CI/CD concepts, monitoring, logging

## 📊 Benefits Demonstrated

- **Time Savings**: 5 minutes daily → Fully automated
- **Reliability**: Never miss optimal booking windows
- **Scalability**: Easy to extend for multiple users
- **Cost Effective**: Runs on minimal GCP resources (~$5/month)
- **Learning**: Practical cloud and automation experience

## 🔧 Configuration

Edit `bot/config.py` to customize:
- Target gym website URL
- User credentials (stored securely)
- Preferred time slots
- Retry attempts and delays
- Notification settings

## 📈 Future Enhancements

- [ ] Multi-gym support
- [ ] Mobile app interface
- [ ] Machine learning for optimal booking times
- [ ] Telegram/Discord bot integration
- [ ] Kubernetes deployment
- [ ] A/B testing for different strategies

---

**Built for demonstrating real-world automation and cloud deployment skills in technical interviews.**