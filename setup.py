#!/usr/bin/env python3
"""
InsightVault Setup Script
Comprehensive setup for new installations and development environments.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def log(message: str, level: str = "INFO"):
    """Log messages with emoji indicators."""
    emoji = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️", 
        "ERROR": "❌"
    }.get(level, "ℹ️")
    print(f"{emoji} {message}")

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        log(f"Python 3.8+ required, found {version.major}.{version.minor}", "ERROR")
        return False
    log(f"Python {version.major}.{version.minor}.{version.micro} ✓", "SUCCESS")
    return True

def check_node_js():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            log(f"Node.js {result.stdout.strip()} ✓", "SUCCESS")
            return True
    except FileNotFoundError:
        pass
    
    log("Node.js not found. Please install Node.js from https://nodejs.org/", "ERROR")
    return False

def check_npm():
    """Check if npm is available."""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            log(f"npm {result.stdout.strip()} ✓", "SUCCESS")
            return True
    except FileNotFoundError:
        pass
    
    log("npm not found. Please install npm.", "ERROR")
    return False

def install_backend_dependencies():
    """Install backend Python dependencies."""
    log("Installing backend dependencies...", "INFO")
    
    try:
        # Try minimal requirements first to avoid Rust compilation issues
        requirements_file = "backend/requirements-minimal.txt"
        if os.path.exists(requirements_file):
            log("Using minimal requirements to avoid compilation issues...", "INFO")
            cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_file]
        else:
            cmd = [sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            log("Backend dependencies installed successfully", "SUCCESS")
            return True
        else:
            log(f"Backend dependency installation failed: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        log(f"Error installing backend dependencies: {e}", "ERROR")
        return False

def install_frontend_dependencies():
    """Install frontend Node.js dependencies."""
    log("Installing frontend dependencies...", "INFO")
    
    try:
        cmd = ["npm", "install"]
        result = subprocess.run(cmd, cwd="frontend", capture_output=True, text=True)
        
        if result.returncode == 0:
            log("Frontend dependencies installed successfully", "SUCCESS")
            return True
        else:
            log(f"Frontend dependency installation failed: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        log(f"Error installing frontend dependencies: {e}", "ERROR")
        return False

def initialize_database():
    """Initialize the database."""
    log("Initializing database...", "INFO")
    
    try:
        cmd = [sys.executable, "init_db.py"]
        result = subprocess.run(cmd, cwd="backend", capture_output=True, text=True)
        
        if result.returncode == 0:
            log("Database initialized successfully", "SUCCESS")
            return True
        else:
            log(f"Database initialization failed: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        log(f"Error initializing database: {e}", "ERROR")
        return False

def create_config_file():
    """Create default configuration file if it doesn't exist."""
    config_file = "config.json"
    if not os.path.exists(config_file):
        log("Creating default configuration file...", "INFO")
        
        default_config = {
            "openai_api_key": "your_openai_api_key_here",
            "model": "gpt-4",
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            log("Default configuration file created", "SUCCESS")
            log("⚠️  Please update config.json with your OpenAI API key", "WARNING")
            return True
        except Exception as e:
            log(f"Error creating config file: {e}", "ERROR")
            return False
    
    log("Configuration file already exists", "INFO")
    return True

def setup_directories():
    """Create necessary directories."""
    log("Setting up directories...", "INFO")
    
    directories = [
        "data",
        "data/cache", 
        "data/analytics_cache",
        "backend/data",
        "backend/data/chat_cache"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    log("Directories created successfully", "SUCCESS")
    return True

def main():
    """Main setup function."""
    print("🚀 InsightVault Setup")
    print("=" * 50)
    
    # Check system requirements
    log("Checking system requirements...", "INFO")
    
    if not check_python_version():
        return False
    
    if not check_node_js():
        return False
    
    if not check_npm():
        return False
    
    # Setup directories
    if not setup_directories():
        return False
    
    # Create config file
    if not create_config_file():
        return False
    
    # Install dependencies
    if not install_backend_dependencies():
        log("⚠️  Backend dependency installation failed, but continuing...", "WARNING")
    
    if not install_frontend_dependencies():
        log("⚠️  Frontend dependency installation failed, but continuing...", "WARNING")
    
    # Initialize database
    if not initialize_database():
        log("⚠️  Database initialization failed, but continuing...", "WARNING")
    
    print("\n" + "=" * 50)
    log("Setup complete!", "SUCCESS")
    print("\nNext steps:")
    print("1. Update config.json with your OpenAI API key")
    print("2. Run 'python insightvault.py' to start the application")
    print("3. Open http://localhost:3000 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 