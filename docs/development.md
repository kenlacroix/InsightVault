# 🛠️ Development Guide

This guide helps developers set up the InsightVault development environment, understand the architecture, and contribute to the project.

## 🏗️ Architecture Overview

InsightVault follows a modern full-stack architecture with clear separation of concerns:

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

| Component      | Technology           | Version | Purpose               |
| -------------- | -------------------- | ------- | --------------------- |
| **Frontend**   | Next.js + TypeScript | 14+     | Modern web interface  |
| **Styling**    | Tailwind CSS         | 3+      | Utility-first CSS     |
| **Backend**    | FastAPI + Python     | 3.8+    | API server            |
| **Database**   | SQLite/PostgreSQL    | -       | Data persistence      |
| **AI**         | OpenAI GPT-4         | -       | Conversation analysis |
| **Deployment** | Docker               | -       | Containerization      |

## 🚀 Development Setup

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **Docker** (optional, for containerized development)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-username/InsightVault.git
cd InsightVault

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Backend Setup

```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# For Windows (if you encounter build issues):
pip install -r backend/requirements-windows.txt

# Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Return to root
cd ..
```

### 4. Database Setup

```bash
# For development (SQLite)
# The database will be created automatically

# For production (PostgreSQL)
# Install PostgreSQL and update backend/.env
```

### 5. Configuration

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

## 🏃‍♂️ Running the Application

### Development Mode

```bash
# Start backend server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal, start frontend
cd frontend
npm run dev
```

### Using the Launcher

```bash
# Quick start with auto-install
python insightvault.py start --auto-install

# Development mode with monitoring
python insightvault.py start --dev --monitor
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run individual services
docker-compose up backend
docker-compose up frontend
```

## 📁 Project Structure

```
InsightVault/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # Next.js app router pages
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   └── lib/             # Utility functions
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   ├── models.py        # Database models
│   │   ├── database.py      # Database configuration
│   │   └── main.py          # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend container
├── shared/                   # Shared TypeScript types
│   └── types.ts             # Common type definitions
├── docs/                     # Documentation
├── tests/                    # Test suite
├── data/                     # Sample data and cache
├── docker-compose.yml        # Docker configuration
└── insightvault.py          # Unified launcher
```

## 🔧 Development Workflow

### Code Style

**Python (Backend):**

- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for all public functions

**TypeScript (Frontend):**

- Use strict TypeScript configuration
- Follow ESLint rules
- Use functional components with hooks
- Prefer named exports over default exports

### Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test

# Run all tests
python -m pytest tests/
```

### Code Quality

```bash
# Backend linting and formatting
cd backend
black .
flake8 .
mypy .

# Frontend linting and formatting
cd frontend
npm run lint
npm run format
```

## 🏗️ Architecture Details

### Backend Architecture

**FastAPI Application Structure:**

```
app/
├── main.py              # FastAPI app initialization
├── config.py            # Configuration management
├── database.py          # Database connection and session
├── models.py            # SQLAlchemy models
├── auth.py              # Authentication middleware
└── api/                 # API route modules
    ├── chat.py          # Chat and conversation endpoints
    ├── files.py         # File upload and management
    └── settings.py      # Application settings
```

**Key Components:**

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **Alembic**: Database migrations
- **OpenAI**: AI integration for conversation analysis

### Frontend Architecture

**Next.js Application Structure:**

```
src/
├── app/                 # Next.js app router
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Home page
│   ├── dashboard/       # Dashboard pages
│   ├── chat/            # Chat interface
│   └── upload/          # File upload
├── components/          # Reusable components
│   ├── ui/              # Base UI components
│   ├── chat/            # Chat-related components
│   └── upload/          # Upload components
├── contexts/            # React contexts
└── lib/                 # Utility functions
```

**Key Technologies:**

- **Next.js 14**: React framework with app router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first styling
- **React Hook Form**: Form handling
- **Zustand**: State management

### Data Flow

1. **File Upload**: Frontend uploads ChatGPT conversation files
2. **Processing**: Backend parses and processes conversation data
3. **AI Analysis**: OpenAI API generates summaries and insights
4. **Storage**: Processed data stored in database
5. **Retrieval**: Frontend fetches and displays processed data
6. **Interaction**: Users can search, filter, and generate insights

## 🔌 API Reference

### Core Endpoints

**File Management:**

- `POST /api/files/upload` - Upload conversation files
- `GET /api/files/list` - List uploaded files
- `DELETE /api/files/{file_id}` - Delete file

**Conversation Processing:**

- `POST /api/chat/process` - Process conversations
- `GET /api/chat/conversations` - List conversations
- `GET /api/chat/conversations/{id}` - Get conversation details

**AI Analysis:**

- `POST /api/chat/summarize` - Generate summaries
- `POST /api/chat/insights` - Generate insights
- `GET /api/chat/search` - Search conversations

### Authentication

Currently using simple API key authentication:

- Add `X-API-Key` header to requests
- Configure in `backend/.env`

## 🧪 Testing Strategy

### Backend Testing

**Unit Tests:**

- Test individual functions and classes
- Mock external dependencies
- Use pytest fixtures for test data

**Integration Tests:**

- Test API endpoints
- Test database operations
- Test external service integration

**Test Structure:**

```
tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
├── fixtures/             # Test data and fixtures
└── conftest.py           # Pytest configuration
```

### Frontend Testing

**Component Tests:**

- Test individual React components
- Use React Testing Library
- Mock API calls and external dependencies

**E2E Tests:**

- Test complete user workflows
- Use Playwright or Cypress
- Test critical user journeys

## 🚀 Deployment

### Development Deployment

```bash
# Using the launcher
python insightvault.py start --prod

# Manual deployment
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
cd frontend && npm run build && npm start
```

### Production Deployment

**Docker Deployment:**

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up --build
```

**Manual Deployment:**

1. Set up production database (PostgreSQL)
2. Configure environment variables
3. Build frontend: `npm run build`
4. Start backend with production server
5. Serve frontend with nginx or similar

## 🤝 Contributing

### Development Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes following the code style guidelines
4. **Test** your changes thoroughly
5. **Commit** with descriptive messages: `git commit -m "feat: add amazing feature"`
6. **Push** to your fork: `git push origin feature/amazing-feature`
7. **Create** a Pull Request

### Pull Request Guidelines

- **Clear Description**: Explain what the PR does and why
- **Tests**: Include tests for new functionality
- **Documentation**: Update docs for new features
- **Code Review**: Address review comments promptly

### Issue Reporting

When reporting issues:

- Use the issue template
- Include system information
- Provide steps to reproduce
- Include error logs and screenshots

## 📚 Additional Resources

- **[API Documentation](api.md)** - Detailed API reference
- **[Architecture Docs](architecture/system-design.md)** - System design details
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Features Guide](features.md)** - User-facing feature documentation

---

_Need help with development? Check the [troubleshooting guide](troubleshooting.md) or open an issue on GitHub._
