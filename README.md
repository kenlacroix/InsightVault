# InsightVault

> **Windows users:**
> For the smoothest backend install, use `requirements-windows.txt`:
>
> ```sh
> pip install -r backend/requirements-windows.txt
> ```
>
> This file contains only the versions and packages confirmed to work on Windows. For Linux/macOS, use `backend/requirements.txt`.

---

(Existing project documentation continues below)

# 🧠 InsightVault - Personal Growth Reflection Tool

A local desktop application that helps you explore and reflect on your personal growth using exported ChatGPT conversations. InsightVault acts like a **digital therapist**, **personal historian**, and **insight engine** to help you find patterns in your dialogues around spirituality, healing, and self-awareness.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![OpenAI](https://img.shields.io/badge/powered%20by-OpenAI%20GPT--4-orange.svg)

## ✨ Features

- **📥 Import ChatGPT Conversations** - Load and parse your exported ChatGPT conversations
- **🤖 AI-Powered Summaries** - Automatically generate titles, summaries, and topic tags using GPT-4
- **🔍 Search & Filter** - Find conversations by keyword, tag, or date range
- **💡 Deep Insights** - Ask reflective questions and get integrated analysis across your conversations
- **📊 Export Options** - Save insights and summaries to Markdown files
- **🏠 Local-First** - All data stays on your computer, privacy-focused design
- **⚡ Smart Caching** - Cache GPT results to save API costs

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Clone or download this repository
git clone <repository-url>
cd insightvault

# Option A: Use the setup script (recommended)
python setup.py

# Option B: Manual installation
# Install PySimpleGUI from private server
pip install --force-reinstall --extra-index-url https://PySimpleGUI.net/install PySimpleGUI>=5.0.10

# Install other dependencies
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

```bash
# Copy the example config file
cp config.json.example config.json

# Edit config.json with your OpenAI API key
{
    "openai_api_key": "your_openai_api_key_here",
    "model": "gpt-4",
    "max_tokens": 1500,
    "temperature": 0.7
}
```

**Get your OpenAI API key:**

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Add it to your `config.json` file

### 3. Prepare Your Data

**Export your ChatGPT conversations:**

1. Go to [ChatGPT Settings](https://chat.openai.com/settings/data-export)
2. Request a data export
3. Download and extract the `conversations.json` file
4. Place it in the `data/` folder (or load it via the GUI)

**Or use sample data:**

- Sample conversations are included in `data/sample_conversations.json`

### 4. Launch the Application

```bash
# Launch GUI (recommended)
python main.py

# Or use command line interface
python main.py --cli

# Show detailed help
python main.py --help-detailed
```

## 🎯 Usage Guide

### Loading Conversations

1. **GUI**: Click "File" → "Load Conversations" and select your `conversations.json` file
2. **CLI**: Enter the file path when prompted

### Exploring Your Data

- **Search**: Type keywords to find relevant conversations
- **Filter by Tag**: Use the dropdown to filter by auto-generated topic tags
- **View Details**: Click any conversation to see summary, tags, and full content

### Generating Insights

1. **Choose a Question**: Select from predefined questions or write your own:

   - "How have I grown spiritually over time?"
   - "What emotional patterns have I been working through?"
   - "How has my relationship with anxiety evolved?"
   - "What breakthroughs have I had regarding childhood trauma?"

2. **Generate Insight**: Click "Generate Insight" to get an AI-powered reflection that includes:

   - **Deep Analysis**: Multi-paragraph reflection on your growth patterns
   - **Meaningful Quotes**: Key excerpts from your conversations
   - **Themes**: Recurring topics and patterns identified
   - **Timeline Insights**: How your perspectives have evolved over time

3. **Export Results**: Save insights as Markdown files for future reference

### AI Features

**Automatic Summarization:**

- Click "Tools" → "Summarize All" to process all conversations
- Generates: Auto-titles, 2-5 sentence summaries, and topic tags
- Results are cached to avoid reprocessing

**Smart Caching:**

- All GPT results are cached locally
- Use "Tools" → "Clear Cache" to force regeneration

## 📁 Project Structure

```
insightvault/
├── main.py                 # App launcher
├── chat_parser.py         # JSON parser and conversation handling
├── summarizer.py          # GPT-4 summarization and tagging
├── insight_engine.py      # Reflective Q&A and insight generation
├── gui.py                 # PySimpleGUI interface
├── config.json           # API key configuration (create from example)
├── config.json.example   # Example configuration
├── requirements.txt      # Python dependencies
├── data/
│   ├── sample_conversations.json
│   └── cache/           # Cached GPT results
├── output/              # Generated insights and summaries
├── LICENSE             # MIT License
└── README.md           # This file
```

## 🔧 Technical Details

### Tech Stack

| Component    | Technology           |
| ------------ | -------------------- |
| **Language** | Python 3.7+          |
| **AI/NLP**   | OpenAI GPT-4 API     |
| **GUI**      | PySimpleGUI          |
| **Data**     | JSON, Pickle (cache) |
| **Export**   | Markdown, CSV        |

### Dependencies

- `openai>=1.3.0` - OpenAI API client
- `PySimpleGUI>=5.0.10` - GUI framework (from private server)
- `python-dateutil>=2.8.0` - Date parsing utilities
- `matplotlib>=3.6.0` - Data visualization
- `seaborn>=0.12.0` - Statistical visualization
- `plotly>=5.13.0` - Interactive charts
- `pandas>=1.5.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing
- `scikit-learn>=1.2.0` - Machine learning
- `textblob>=0.17.0` - Sentiment analysis

### Data Privacy

- **Local-First**: All conversations stay on your computer
- **No Cloud Storage**: No external databases or cloud services
- **API Usage**: Only sends conversation text to OpenAI for analysis
- **Caching**: Results cached locally to minimize API calls

## 💡 Sample Reflective Questions

**Spiritual Growth:**

- "How has my spiritual practice evolved over time?"
- "What insights have I gained about my relationship with the divine?"
- "How have I grown in mindfulness and presence?"

**Emotional Healing:**

- "What patterns do I see in my emotional responses?"
- "How has my relationship with difficult emotions changed?"
- "What breakthroughs have I had in therapy or self-work?"

**Personal Development:**

- "How has my sense of identity and self-worth evolved?"
- "What have I learned about setting boundaries?"
- "How have my perspectives on relationships developed?"

**Life Direction:**

- "What insights have I gained about my life purpose?"
- "How have my values and priorities shifted?"
- "What patterns do I see in my decision-making?"

## 🛠 Development

### Running Tests

```bash
# Test the parser with sample data
python chat_parser.py

# Test the summarizer
python summarizer.py

# Test the insight engine
python insight_engine.py
```

### Extending the Application

The modular design makes it easy to extend:

- **Add new export formats** in `summarizer.py` and `insight_engine.py`
- **Customize prompts** in the `_create_summary_prompt()` and `_create_insight_prompt()` methods
- **Add new GUI features** in `gui.py`
- **Support other data formats** by extending `chat_parser.py`

## ❓ Troubleshooting

### Common Issues

**"Import error: No module named 'openai'"**

```bash
pip install -r requirements.txt
```

**"Config file not found"**

```bash
cp config.json.example config.json
# Then edit config.json with your API key
```

**"Failed to load conversations"**

- Ensure your JSON file is valid ChatGPT export format
- Try with the sample data first: `data/sample_conversations.json`

**"AI components not available"**

- Check that your OpenAI API key is valid and has credits
- Verify your `config.json` format matches the example

### Getting Help

1. Check the detailed help: `python main.py --help-detailed`
2. Try the CLI mode for debugging: `python main.py --cli`
3. Test with sample data first
4. Check your OpenAI API key and account credits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**What this means:**

- ✅ Free for commercial and personal use
- ✅ You can modify, distribute, and build on it
- ✅ No warranty or liability
- ✅ Must include original license notice

## 🤝 Contributing

Contributions are welcome! This project aims to help people gain insights into their personal growth journey. Here are some ways to contribute:

- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new reflection prompts or analysis features
- **Code Contributions**: Improve the codebase, add tests, or optimize performance
- **Documentation**: Help improve setup instructions or usage guides

## 🙏 Acknowledgments

- **OpenAI** for providing the GPT-4 API that powers the insights
- **PySimpleGUI** for making desktop GUI development accessible
- **ChatGPT Users** who inspired this tool through their personal growth journeys

---

**Happy reflecting!** 🌱 May this tool help you discover meaningful patterns in your personal growth journey.
