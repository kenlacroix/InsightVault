# 🚀 Getting Started with InsightVault

This guide will help you get InsightVault up and running quickly on your system.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)
- **OpenAI API Key** - [Get API Key](https://platform.openai.com/api-keys)

## 🛠️ Installation Options

### Option 1: Quick Start (Recommended)

Use our unified launcher for the easiest setup:

```bash
# Clone the repository
git clone https://github.com/your-username/InsightVault.git
cd InsightVault

# Run the unified launcher
python insightvault.py start --auto-install
```

The launcher will:

- ✅ Check system requirements
- ✅ Install dependencies automatically
- ✅ Start both backend and frontend servers
- ✅ Open the application in your browser

### Option 2: Manual Installation

If you prefer manual control or encounter issues:

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/InsightVault.git
cd InsightVault
```

#### 2. Set Up Backend

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install backend dependencies
# Windows (recommended):
pip install -r backend/requirements-windows.txt
# macOS/Linux:
pip install -r backend/requirements.txt
```

#### 3. Set Up Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Return to root
cd ..
```

#### 4. Configure Environment

```bash
# Copy configuration template
cp config.json.example config.json

# Edit config.json with your OpenAI API key
{
    "openai_api_key": "your_openai_api_key_here",
    "model": "gpt-4",
    "max_tokens": 1500,
    "temperature": 0.7
}
```

#### 5. Start the Application

```bash
# Start backend server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal, start frontend
cd frontend
npm run dev
```

## 🔑 Getting Your OpenAI API Key

1. **Visit OpenAI Platform**: Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. **Sign In**: Use your OpenAI account (create one if needed)
3. **Create API Key**: Click "Create new secret key"
4. **Copy Key**: Copy the generated key (it starts with `sk-`)
5. **Add to Config**: Paste it in your `config.json` file

> **⚠️ Security Note**: Never commit your API key to version control. The `config.json` file is already in `.gitignore`.

## 📁 Preparing Your Data

### Export ChatGPT Conversations

1. **Go to ChatGPT Settings**: Visit [ChatGPT Data Export](https://chat.openai.com/settings/data-export)
2. **Request Export**: Click "Export data" and wait for the email
3. **Download**: Download the `conversations.json` file from the email
4. **Place in Project**: Put the file in the `data/` folder

### Sample Data

If you don't have ChatGPT exports yet, you can use the included sample data:

```bash
# Sample conversations are available at:
data/sample_conversations.json
```

## 🌐 Accessing the Application

Once everything is running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 First Steps

1. **Upload Conversations**: Use the file upload interface to load your ChatGPT exports
2. **Generate Summaries**: Click "Summarize All" to process your conversations
3. **Explore Insights**: Use the search and filter features to explore your data
4. **Ask Questions**: Try asking reflective questions like "How have I grown spiritually?"

## 🔧 Troubleshooting

### Common Issues

#### Python/Backend Issues

**"Module not found" errors:**

```bash
# Ensure you're in the virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r backend/requirements.txt
```

**Port 8000 already in use:**

```bash
# Use the launcher to clean up ports
python insightvault.py cleanup

# Or manually kill the process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### Node.js/Frontend Issues

**"npm not found" error:**

```bash
# Ensure Node.js is installed and in PATH
node --version
npm --version

# If npm not found, reinstall Node.js and check "Add to PATH"
```

**Port 3000 already in use:**

```bash
# Use the launcher to clean up ports
python insightvault.py cleanup

# Or manually kill the process
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

#### API Key Issues

**"Invalid API key" error:**

- Verify your API key is correct in `config.json`
- Ensure you have sufficient OpenAI credits
- Check that the key starts with `sk-`

### Getting Help

1. **Check the [Troubleshooting Guide](troubleshooting.md)** for detailed solutions
2. **Run Diagnostics**: `python insightvault.py diagnostics`
3. **Check Logs**: Look for error messages in the terminal
4. **Open an Issue**: Report bugs on GitHub with system details

## 🚀 Next Steps

Now that you have InsightVault running:

- **[Features Guide](features.md)** - Learn how to use all features
- **[Development Guide](development.md)** - Set up for development
- **[API Reference](api.md)** - Understand the backend API

## 📞 Support

- **Documentation**: Check the [main docs](README.md)
- **Issues**: [GitHub Issues](https://github.com/your-username/InsightVault/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/InsightVault/discussions)

---

_Need help? Check the [troubleshooting guide](troubleshooting.md) or open an issue on GitHub._
