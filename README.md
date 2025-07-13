# 🧠 InsightVault - Personal Growth Reflection Tool

A modern web application that helps you explore and reflect on your personal growth using exported ChatGPT conversations. InsightVault acts like a **digital therapist**, **personal historian**, and **insight engine** to help you find patterns in your dialogues around spirituality, healing, and self-awareness.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)
![OpenAI](https://img.shields.io/badge/powered%20by-OpenAI%20GPT--4-orange.svg)

## ✨ Features

- **📥 Import ChatGPT Conversations** - Load and parse your exported ChatGPT conversations
- **🤖 AI-Powered Analysis** - Generate titles, summaries, and insights using GPT-4
- **🔍 Advanced Search & Filter** - Find conversations by keyword, tag, or date range
- **💡 Deep Insights** - Ask reflective questions and get comprehensive analysis
- **📊 Analytics Dashboard** - Visualize your growth patterns and trends
- **🏠 Local-First** - All data stays on your computer, privacy-focused design
- **⚡ Smart Caching** - Cache GPT results to save API costs
- **🌐 Modern Web Interface** - Responsive design with real-time updates

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/InsightVault.git
cd InsightVault

# Run the setup script
python setup.py

# Start the application
python insightvault.py
```

The setup script will:

- ✅ Check system requirements (Python 3.8+, Node.js, npm)
- ✅ Create necessary directories and configuration files
- ✅ Install backend and frontend dependencies
- ✅ Initialize the database automatically
- ✅ Set up default configuration

### Option 2: Manual Setup

```bash
# 1. Install backend dependencies (use minimal requirements on Windows)
cd backend
pip install -r requirements-minimal.txt  # or requirements.txt

# 2. Install frontend dependencies
cd ../frontend
npm install
cd ..

# 3. Initialize the database
cd backend
python init_db.py
cd ..

# 4. Configure OpenAI API key
cp config.json.example config.json
# Edit config.json with your OpenAI API key

# 5. Start the application
python insightvault.py
```

### First-Time Setup Notes

- **Database**: Tables are created automatically on first startup
- **Configuration**: Update `config.json` with your OpenAI API key before using AI features
- **Branch Merges**: If you encounter database errors after merging branches, run `python backend/init_db.py`
- **Windows Users**: Use `requirements-minimal.txt` to avoid Rust compilation issues

## 🔑 Getting Your OpenAI API Key

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Add it to your `config.json` file

> **⚠️ Security Note**: Never commit your API key to version control. The `config.json` file is already in `.gitignore`.

## 📁 Preparing Your Data

### Export ChatGPT Conversations

1. Go to [ChatGPT Data Export](https://chat.openai.com/settings/data-export)
2. Request a data export
3. Download the `conversations.json` file
4. Upload it through the web interface

### Sample Data

Sample conversations are included in `data/sample_conversations.json` for testing.

## 🌐 Accessing the Application

Once running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Usage Guide

### 1. Upload Conversations

Use the file upload interface to load your ChatGPT exports.

### 2. Generate Summaries

Click "Summarize All" to process your conversations with AI.

### 3. Explore Insights

- **Search**: Find conversations by keywords
- **Filter**: Use tags and date ranges
- **Ask Questions**: Generate insights about your growth

### 4. Export Results

Save insights as Markdown files for journaling.

## 🏗️ Architecture

InsightVault uses a modern full-stack architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • React/TS      │    │ • Python        │    │ • OpenAI API    │
│ • Tailwind CSS  │    │ • FastAPI       │    │ • Database      │
│ • Next.js       │    │ • SQLAlchemy    │    │ • File Storage  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

| Component      | Technology           | Purpose               |
| -------------- | -------------------- | --------------------- |
| **Frontend**   | Next.js + TypeScript | Modern web interface  |
| **Styling**    | Tailwind CSS         | Utility-first CSS     |
| **Backend**    | FastAPI + Python     | API server            |
| **Database**   | SQLite/PostgreSQL    | Data persistence      |
| **AI**         | OpenAI GPT-4         | Conversation analysis |
| **Deployment** | Docker               | Containerization      |

## 📁 Project Structure

```
InsightVault/
├── frontend/           # Next.js web application
├── backend/            # FastAPI backend server
├── shared/             # Shared TypeScript types
├── docs/               # Documentation
├── data/               # Sample data and cache
├── tests/              # Test suite
├── docker-compose.yml  # Docker configuration
└── insightvault.py     # Unified launcher
```

## 📚 Documentation

- **[Getting Started](docs/getting-started.md)** - Installation and setup guide
- **[Features Guide](docs/features.md)** - Complete feature documentation
- **[Development Guide](docs/development.md)** - Development setup and architecture
- **[API Reference](docs/api.md)** - Backend API documentation
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🔧 Development

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### Environment Notes

**Windows Development Environment:**

- This project is configured for Windows/PowerShell
- Use `;` for command chaining instead of `&&`
- Use `dir` instead of `ls` for listing files
- Use Windows path separators (`\`)

**Example Commands:**

```powershell
# ✅ Correct (PowerShell)
cd backend; python -m uvicorn app.main:app --reload
cd frontend; npm run dev

# ❌ Incorrect (Bash)
cd backend && python -m uvicorn app.main:app --reload
```

### Development Setup

```bash
# Clone and setup
git clone https://github.com/your-username/InsightVault.git
cd InsightVault

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# Start development servers
python insightvault.py start --dev
```

### Running Tests

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment

1. Set up production database (PostgreSQL)
2. Configure environment variables
3. Build frontend: `npm run build`
4. Start backend with production server
5. Serve frontend with nginx or similar

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the code style guidelines
4. Test your changes thoroughly
5. Commit with descriptive messages: `git commit -m "feat: add amazing feature"`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs folder](docs/) for comprehensive guides
- **Issues**: [Report bugs and request features](https://github.com/your-username/InsightVault/issues)
- **Discussions**: [Ask questions and get help](https://github.com/your-username/InsightVault/discussions)

## 🔄 Changelog

### Recent Updates

- **Unified Launcher**: Single command to start the entire application
- **Modern Web Interface**: Replaced desktop GUI with responsive web app
- **Enhanced Documentation**: Comprehensive guides and troubleshooting
- **Improved Architecture**: FastAPI backend with Next.js frontend
- **Better Error Handling**: Robust startup and diagnostic tools

---

_InsightVault is designed to help you discover patterns in your personal growth journey through AI-powered analysis of your ChatGPT conversations._
