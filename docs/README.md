# 📚 InsightVault Documentation

Welcome to the InsightVault documentation! This guide will help you understand, install, and use InsightVault effectively.

## 🚀 Quick Navigation

- **[Getting Started](getting-started.md)** - Installation, setup, and first steps
- **[Features & Usage](features.md)** - Complete feature guide and examples
- **[Development Guide](development.md)** - Architecture, development setup, and contributing
- **[API Reference](api.md)** - Backend API documentation
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## 🧠 What is InsightVault?

InsightVault is a **personal growth reflection tool** that analyzes your ChatGPT conversations to help you discover patterns in your spiritual growth, emotional development, and healing journey. Think of it as a **digital therapist** and **personal historian** that works with your conversation data.

### Key Capabilities

- **📥 Import ChatGPT Conversations** - Load and parse your exported conversations
- **🤖 AI-Powered Analysis** - Generate summaries, tags, and insights using GPT-4
- **🔍 Smart Search & Filter** - Find conversations by keywords, tags, or date ranges
- **💡 Deep Insights** - Ask reflective questions and get comprehensive analysis
- **📊 Export & Share** - Save insights as Markdown files for journaling
- **🔒 Privacy-First** - All data stays on your computer

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Services   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (OpenAI)      │
│                 │    │                 │    │                 │
│ • Chat Interface│    │ • File Upload   │    │ • GPT-4 API     │
│ • Analytics     │    │ • Data Storage  │    │ • Summarization │
│ • User Auth     │    │ • Search Engine │    │ • Insight Gen   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
InsightVault/
├── frontend/           # Next.js web application
├── backend/            # FastAPI backend server
├── shared/             # Shared TypeScript types
├── docs/               # Documentation (this folder)
├── data/               # Sample data and cache
├── tests/              # Test suite
└── docker/             # Docker configuration
```

## 🎯 Use Cases

### Personal Growth Enthusiasts

- Track your spiritual development over time
- Identify patterns in your emotional healing journey
- Generate insights for therapy sessions
- Create personal growth journals

### Researchers & Therapists

- Analyze conversation patterns for research
- Generate insights for client sessions
- Export structured data for analysis
- Maintain privacy with local processing

### Developers

- Extend the platform with new features
- Integrate with other personal growth tools
- Contribute to the open-source project

## 🔧 Technology Stack

| Component      | Technology           | Purpose                        |
| -------------- | -------------------- | ------------------------------ |
| **Frontend**   | Next.js + TypeScript | Modern web interface           |
| **Backend**    | FastAPI + Python     | API server and data processing |
| **Database**   | SQLite/PostgreSQL    | Data storage                   |
| **AI**         | OpenAI GPT-4         | Conversation analysis          |
| **Deployment** | Docker               | Containerized deployment       |

## 📖 Documentation Sections

### For Users

- **[Getting Started](getting-started.md)** - Quick setup guide
- **[Features & Usage](features.md)** - How to use InsightVault
- **[Troubleshooting](troubleshooting.md)** - Solve common problems

### For Developers

- **[Development Guide](development.md)** - Setup development environment
- **[API Reference](api.md)** - Backend API documentation
- **[Architecture](architecture/system-design.md)** - System design details

### For Contributors

- **[Contributing Guidelines](development.md#contributing)** - How to contribute
- **[Code Style](development.md#code-style)** - Coding standards
- **[Testing](development.md#testing)** - Testing guidelines

## 🆘 Need Help?

1. **Check the [Troubleshooting Guide](troubleshooting.md)** for common solutions
2. **Review the [Getting Started Guide](getting-started.md)** for setup help
3. **Explore the [Features Guide](features.md)** for usage examples
4. **Open an issue** on GitHub for bugs or feature requests

## 📄 License

InsightVault is open-source software licensed under the [MIT License](../LICENSE).

---

_This documentation is maintained by the InsightVault community. For the latest updates, check the [GitHub repository](https://github.com/your-username/InsightVault)._
