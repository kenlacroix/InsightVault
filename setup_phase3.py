#!/usr/bin/env python3
"""
Setup script for InsightVault Phase 3
Handles installation of dependencies and initial configuration.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

def setup_backend():
    """Setup backend dependencies."""
    print("\n🔧 Setting up backend...")
    
    # Check if we're on Windows
    is_windows = platform.system() == "Windows"
    
    if is_windows:
        print("📝 Detected Windows - using Windows-compatible requirements")
        requirements_file = "backend/requirements-windows.txt"
    else:
        requirements_file = "backend/requirements.txt"
    
    # Install Python dependencies
    result = run_command(f"pip install -r {requirements_file}")
    if not result:
        print("⚠️  Some dependencies may have failed to install")
        print("   You can try installing them manually or use the alternative requirements file")

def setup_frontend():
    """Setup frontend dependencies."""
    print("\n🔧 Setting up frontend...")
    
    # Check if Node.js is installed
    node_result = run_command("node --version")
    if not node_result:
        print("❌ Node.js is not installed. Please install Node.js 18+ first.")
        return False
    
    # Check if npm is installed
    npm_result = run_command("npm --version")
    if not npm_result:
        print("❌ npm is not installed. Please install npm first.")
        return False
    
    # Install frontend dependencies
    result = run_command("npm install", cwd="frontend")
    if not result:
        print("❌ Frontend dependencies installation failed")
        return False
    
    return True

def create_env_files():
    """Create environment files if they don't exist."""
    print("\n📝 Creating environment files...")
    
    # Backend .env
    backend_env = Path("backend/.env")
    if not backend_env.exists():
        backend_env.write_text("""# InsightVault Phase 3 Backend Configuration

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/insightvault
# For development with SQLite, uncomment the line below:
# USE_SQLITE=true

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Redis Configuration (for Celery)
REDIS_URL=redis://localhost:6379

# Development Settings
DEBUG=true
DB_ECHO=false
""")
        print("✅ Created backend/.env")
    
    # Frontend .env.local
    frontend_env = Path("frontend/.env.local")
    if not frontend_env.exists():
        frontend_env.write_text("""# InsightVault Phase 3 Frontend Configuration

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=InsightVault

# Development Settings
NODE_ENV=development
""")
        print("✅ Created frontend/.env.local")

def main():
    """Main setup function."""
    print("🚀 InsightVault Phase 3 Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Setup backend
    setup_backend()
    
    # Setup frontend
    frontend_success = setup_frontend()
    
    # Create environment files
    create_env_files()
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed!")
    
    if frontend_success:
        print("\n📋 Next steps:")
        print("1. Configure your environment variables in backend/.env and frontend/.env.local")
        print("2. Set up your database (PostgreSQL or SQLite)")
        print("3. Run the development servers:")
        print("   - Backend: cd backend && uvicorn app.main:app --reload")
        print("   - Frontend: cd frontend && npm run dev")
        print("\n📚 For more information, see PHASE_3_README.md")
    else:
        print("\n⚠️  Frontend setup failed. Please check the errors above.")
        print("   You may need to install Node.js and npm first.")

if __name__ == "__main__":
    main() 