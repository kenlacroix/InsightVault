# 🚀 InsightVault Startup Scripts

This directory contains several scripts to help you start InsightVault easily on different platforms.

## 📋 Prerequisites

Before running any startup script, make sure you have:

- **Python 3.8+** installed
- **Node.js** and **npm** installed
- **Git** (for cloning the repository)

## 🎯 Quick Start

### Option 1: Cross-Platform Python Script (Recommended)

```bash
# Run the cross-platform launcher
python start_insightvault.py
```

This script works on **Windows**, **macOS**, and **Linux** and provides:

- ✅ Automatic dependency checking
- ✅ Cross-platform compatibility
- ✅ Error monitoring and reporting
- ✅ Clean shutdown handling
- ✅ Interactive dependency installation

### Option 2: Platform-Specific Scripts

#### Windows

```cmd
# Double-click the batch file or run in Command Prompt
start_insightvault.bat
```

#### macOS/Linux

```bash
# Make executable (first time only)
chmod +x start_insightvault.sh

# Run the script
./start_insightvault.sh
```

## 🔧 What the Scripts Do

### 1. **Dependency Checking**

- Verifies Python 3.8+ is installed
- Checks for Node.js and npm
- Validates project structure
- Warns about missing config.json

### 2. **Dependency Installation**

- Installs Python packages from `backend/requirements.txt`
- Installs Node.js packages from `frontend/package.json`
- Uses Windows-specific requirements when available

### 3. **Service Startup**

- Starts the FastAPI backend server on port 8000
- Starts the Next.js frontend server on port 3000
- Opens services in separate windows (Windows) or background (Unix)

### 4. **Health Monitoring**

- Monitors both services for crashes
- Reports errors and status updates
- Provides clean shutdown on Ctrl+C

## 🌐 Accessing InsightVault

Once the scripts complete successfully, you can access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## ⚠️ Troubleshooting

### Common Issues

#### 1. **"Python not found"**

```bash
# Install Python from https://python.org
# Make sure it's added to PATH
```

#### 2. **"Node.js not found"**

```bash
# Install Node.js from https://nodejs.org
# Make sure npm is included
```

#### 3. **"Backend directory not found"**

```bash
# Make sure you're in the InsightVault root directory
# The directory should contain both 'backend' and 'frontend' folders
```

#### 4. **"Port already in use"**

```bash
# Check if something is running on ports 3000 or 8000
# Kill existing processes or change ports in the scripts
```

#### 5. **"Dependencies failed to install"**

```bash
# Try installing manually:
pip install -r backend/requirements.txt
cd frontend && npm install
```

### Windows-Specific Issues

#### **"uvicorn not found"**

```cmd
# Install uvicorn manually
pip install uvicorn fastapi
```

#### **"npm command not recognized"**

```cmd
# Reinstall Node.js and make sure to check "Add to PATH" during installation
```

### Unix-Specific Issues

#### **"Permission denied"**

```bash
# Make scripts executable
chmod +x start_insightvault.sh
```

#### **"python3 not found"**

```bash
# Install Python 3
sudo apt install python3 python3-pip  # Ubuntu/Debian
brew install python3                  # macOS
```

## 🔄 Stopping InsightVault

### Using the Python Script

- Press **Ctrl+C** in the terminal where you ran the script
- The script will automatically stop both services

### Using Platform Scripts

- **Windows**: Close the command prompt windows for each service
- **Unix**: Press **Ctrl+C** in the terminal where you ran the script

## 📝 Configuration

### Setting up OpenAI API Key

1. Copy the example config:

   ```bash
   cp config.json.example config.json
   ```

2. Edit `config.json` and add your OpenAI API key:
   ```json
   {
     "openai_api_key": "your_api_key_here",
     "model": "gpt-4",
     "max_tokens": 1500,
     "temperature": 0.7
   }
   ```

### Customizing Ports

To change the default ports, edit the startup scripts:

- **Backend port**: Change `--port 8000` in the uvicorn command
- **Frontend port**: Change the port in `frontend/package.json` dev script

## 🎉 Success Indicators

When InsightVault starts successfully, you should see:

```
[HH:MM:SS] SUCCESS: 🎉 InsightVault is ready!
[HH:MM:SS] INFO: Frontend: http://localhost:3000
[HH:MM:SS] INFO: Backend: http://localhost:8000
[HH:MM:SS] INFO: Press Ctrl+C to stop all services
```

## 📞 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Look at the error messages in the terminal
3. Verify all prerequisites are installed
4. Try running the services manually to isolate the issue

For additional help, check the main README.md file or create an issue in the repository.
