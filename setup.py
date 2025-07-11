#!/usr/bin/env python3
"""
Setup script for InsightVault
Handles installation of dependencies including PySimpleGUI from private server
"""

import subprocess
import sys
import os

def install_pysimplegui():
    """Install PySimpleGUI from the private server"""
    print("Installing PySimpleGUI from private server...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--force-reinstall", 
            "--extra-index-url", "https://PySimpleGUI.net/install", 
            "PySimpleGUI>=5.0.10"
        ])
        print("✅ PySimpleGUI installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install PySimpleGUI: {e}")
        return False

def install_requirements():
    """Install other requirements"""
    print("Installing other requirements...")
    try:
        # Install requirements excluding PySimpleGUI
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "openai>=1.3.0",
            "python-dateutil>=2.8.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-asyncio>=0.21.0",
            "matplotlib>=3.6.0",
            "seaborn>=0.12.0",
            "plotly>=5.13.0",
            "pandas>=1.5.0",
            "numpy>=1.24.0",
            "scikit-learn>=1.2.0",
            "fpdf2>=2.7.0",
            "reportlab>=3.6.0",
            "textblob>=0.17.0"
        ])
        print("✅ Other requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_config():
    """Set up configuration file if it doesn't exist"""
    if not os.path.exists('config.json'):
        if os.path.exists('config.json.example'):
            import shutil
            shutil.copy('config.json.example', 'config.json')
            print("✅ Created config.json from template")
            print("⚠️  Please edit config.json with your OpenAI API key")
        else:
            print("❌ config.json.example not found")
            return False
    return True

def main():
    """Main setup function"""
    print("🧠 InsightVault Setup")
    print("=" * 50)
    
    # Install PySimpleGUI first
    if not install_pysimplegui():
        return False
    
    # Install other requirements
    if not install_requirements():
        return False
    
    # Setup configuration
    if not setup_config():
        return False
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit config.json with your OpenAI API key")
    print("2. Run: python main.py")
    print("3. Or run: python main.py --cli for command line interface")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 