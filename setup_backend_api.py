#!/usr/bin/env python3
"""
Setup script for InsightVault backend API configuration
"""

import os
import json
import sys

def setup_openai_api():
    """Set up OpenAI API key for the backend"""
    print("🔧 InsightVault Backend API Setup")
    print("=" * 50)
    
    # Check if config.json exists
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            current_key = config.get('openai_api_key', '')
            if current_key and current_key != "your_openai_api_key_here":
                print(f"✅ API key already configured: {current_key[:10]}...")
                choice = input("Do you want to update it? (y/n): ").lower()
                if choice != 'y':
                    return True
        except Exception as e:
            print(f"Error reading config: {e}")
    
    # Get API key from user
    print("\n📝 Please enter your OpenAI API key:")
    print("   (Get it from: https://platform.openai.com/api-keys)")
    print("   (The key should start with 'sk-')")
    
    api_key = input("\nAPI Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format. Should start with 'sk-'")
        return False
    
    # Update config.json
    try:
        config_data = {
            "openai_api_key": api_key,
            "model": "gpt-4",
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=4)
        
        print(f"✅ API key saved to {config_file}")
        
        # Set environment variable for current session
        os.environ['OPENAI_API_KEY'] = api_key
        print("✅ Environment variable set for current session")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return False

def test_api_key():
    """Test the API key"""
    print("\n🧪 Testing API key...")
    
    try:
        import openai
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        # Make a simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        print("✅ API key is valid!")
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("Welcome to InsightVault Backend Setup!")
    
    # Setup API key
    if not setup_openai_api():
        print("\n❌ Setup failed. Please try again.")
        sys.exit(1)
    
    # Test API key
    if test_api_key():
        print("\n🎉 Setup complete! Your backend is ready to use ChatGPT features.")
        print("\n📋 Next steps:")
        print("   1. Restart your backend server")
        print("   2. Go to http://localhost:3000/assistant")
        print("   3. Start chatting with AI-powered insights!")
    else:
        print("\n⚠️ Setup completed but API key test failed.")
        print("   The backend will use fallback responses until the API key is fixed.")

if __name__ == "__main__":
    main() 