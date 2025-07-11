# 🚀 InsightVault Installation Guide

## Quick Installation

### Option 1: Automated Setup (Recommended)

```bash
python setup.py
```

### Option 2: Manual Installation

```bash
# Install PySimpleGUI from private server
pip install --force-reinstall --extra-index-url https://PySimpleGUI.net/install PySimpleGUI>=5.0.10

# Install other dependencies
pip install -r requirements.txt

# Copy configuration template
cp config.json.example config.json
```

## 🔧 Troubleshooting

### PySimpleGUI Issues

If you see errors like `module 'PySimpleGUI' has no attribute 'theme'`:

1. **Uninstall current version:**

   ```bash
   pip uninstall PySimpleGUI
   ```

2. **Install from private server:**
   ```bash
   pip install --force-reinstall --extra-index-url https://PySimpleGUI.net/install PySimpleGUI>=5.0.10
   ```

### API Key Issues

1. **Get your OpenAI API key** from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Edit config.json** and add your key:
   ```json
   {
     "openai_api_key": "your_actual_api_key_here",
     "model": "gpt-4",
     "max_tokens": 1500,
     "temperature": 0.7
   }
   ```

### Import Errors

If you get import errors:

```bash
# Reinstall all dependencies
pip install -r requirements.txt

# Or use the setup script
python setup.py
```

## 🎯 First Run

1. **Configure API key** in `config.json`
2. **Run the application:**
   ```bash
   python main.py          # GUI mode
   python main.py --cli    # Command line mode
   ```
3. **Load your data:**
   - Export conversations from ChatGPT
   - Place `conversations.json` in the `data/` folder
   - Or use the sample data included

## 📁 File Structure After Installation

```
insightvault/
├── main.py                 # Main application
├── setup.py               # Installation script
├── config.json            # Your API configuration
├── config.json.example    # Template configuration
├── requirements.txt       # Dependencies list
├── data/
│   ├── sample_conversations.json
│   ├── cache/            # Cached API responses
│   └── analytics_cache/  # Analytics data cache
├── output/               # Generated reports
└── tests/                # Test suite
```

## 🧪 Testing Installation

Run the test suite to verify everything works:

```bash
python -m pytest tests/ --cov=. --cov-report=term-missing
```

Expected results:

- **94+ tests passing** (93%+ success rate)
- **80%+ code coverage**
- No PySimpleGUI errors

## 🆘 Still Having Issues?

1. **Check Python version:** Requires Python 3.7+
2. **Verify pip installation:** `pip --version`
3. **Clear pip cache:** `pip cache purge`
4. **Use virtual environment:**
   ```bash
   python -m venv insightvault_env
   source insightvault_env/bin/activate  # Linux/Mac
   insightvault_env\Scripts\activate     # Windows
   ```

## 📞 Support

If you continue to have issues:

1. Check the [main README.md](README.md) for detailed usage
2. Review the [troubleshooting section](README.md#troubleshooting)
3. Ensure all dependencies are correctly installed
