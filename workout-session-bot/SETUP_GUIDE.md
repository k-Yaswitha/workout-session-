# 🚀 Setup Guide - Workout Session Reservation Bot

## 📋 Prerequisites

### Required Software
- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Google Chrome** ([Download](https://www.google.com/chrome/))
- **Git** ([Download](https://git-scm.com/downloads))

### For Development
- **Visual Studio Code** ([Download](https://code.visualstudio.com/))
- **PyCharm** (Optional alternative)

## 🔧 Quick Setup (Windows/macOS/Linux)

### 1. Extract and Open Project
```bash
# Extract the zip file to your desired location
# Open terminal/command prompt in the project directory
cd workout-session-bot
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install bot dependencies
cd bot
pip install -r requirements.txt
cd ..

# Install website dependencies
cd demo_website
pip install -r requirements.txt
cd ..
```

### 4. Run the Demo
```bash
# Make run script executable (macOS/Linux)
chmod +x run_demo.sh

# Run the complete demo
./run_demo.sh

# Or run manually:
# Terminal 1: Start website
cd demo_website
python app.py

# Terminal 2: Test bot (after website is running)
cd bot
python test_bot.py --mode full
```

## 🏗️ Visual Studio Code Setup

### 1. Open Project
- Open VS Code
- File → Open Folder → Select `workout-session-bot` folder

### 2. Install Recommended Extensions
```json
// .vscode/extensions.json (auto-suggested)
{
    "recommendations": [
        "ms-python.python",
        "ms-python.pylint",
        "ms-python.black-formatter",
        "ms-vscode.vscode-json",
        "bradlc.vscode-tailwindcss",
        "ms-vscode.live-server"
    ]
}
```

### 3. Configure Python Interpreter
- `Ctrl/Cmd + Shift + P` → "Python: Select Interpreter"
- Choose: `./venv/bin/python` (or `.\venv\Scripts\python.exe` on Windows)

### 4. VS Code Settings
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": false
    }
}
```

### 5. Debug Configuration
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Bot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/bot/reservation_bot.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/bot"
        },
        {
            "name": "Run Demo Website",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/demo_website/app.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/demo_website"
        },
        {
            "name": "Test Bot Configuration",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/bot/test_bot.py",
            "args": ["--mode", "config"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/bot"
        }
    ]
}
```

## 🐍 PyCharm Setup

### 1. Open Project
- File → Open → Select `workout-session-bot` folder

### 2. Configure Interpreter
- File → Settings → Project → Python Interpreter
- Add → Existing Environment → `./venv/bin/python`

### 3. Run Configurations
- Run → Edit Configurations → Add New → Python
  - **Bot**: Script path: `bot/reservation_bot.py`, Working directory: `bot/`
  - **Website**: Script path: `demo_website/app.py`, Working directory: `demo_website/`

## 🌐 Browser Setup for Development

### Chrome Developer Mode
```bash
# For bot testing without headless mode
# Edit bot/config.py:
HEADLESS_MODE = False  # Set to False for debugging
```

### Install ChromeDriver
```bash
# Windows (using chocolatey)
choco install chromedriver

# macOS (using homebrew)
brew install chromedriver

# Linux (manual)
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
```

## 🧪 Testing the Setup

### 1. Test Configuration
```bash
cd bot
python test_bot.py --mode config
```

### 2. Test Website
```bash
cd demo_website
python app.py
# Visit http://localhost:5000
# Login: demo_user / demo_password
```

### 3. Test Full Automation
```bash
# With website running:
cd bot
python test_bot.py --mode full
```

## 🚨 Troubleshooting

### Common Issues

**ChromeDriver not found:**
```bash
# Add to PATH or install:
pip install webdriver-manager
```

**Module not found errors:**
```bash
# Ensure virtual environment is activated:
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

**Port 5000 already in use:**
```bash
# Change port in demo_website/app.py:
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Selenium errors:**
- Update Chrome browser to latest version
- Ensure ChromeDriver version matches Chrome version
- Check firewall/antivirus blocking WebDriver

## 📱 Development Workflow

### 1. Code Changes
- Edit files in VS Code/PyCharm
- Test with `python test_bot.py --mode config`

### 2. Website Development
- Edit templates in `demo_website/templates/`
- Edit styles in `demo_website/static/css/style.css`
- Restart Flask app to see changes

### 3. Bot Development
- Edit logic in `bot/reservation_bot.py`
- Test with website running
- Use `HEADLESS_MODE = False` for visual debugging

### 4. Deployment Testing
- Test with `deployment/setup_vm.sh` on local VM
- Verify cron scheduling
- Check logs and monitoring

## 🎯 Next Steps

1. **Customize for your gym:** Edit `bot/config.py`
2. **Deploy to cloud:** Use `deployment/setup_vm.sh`
3. **Add features:** Extend bot logic or website
4. **Monitor:** Set up email notifications

## 📞 Support

- Check logs in `logs/` directory
- Review error screenshots in `logs/screenshots/`
- Test individual components with `test_bot.py`

---

**Happy Coding! 🎉**