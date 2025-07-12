# 🔧 Troubleshooting Guide

This guide helps you resolve common issues when using InsightVault. If you don't find your issue here, please open an issue on GitHub with detailed information.

## 🚨 Quick Fixes

### Application Won't Start

**Problem**: The application fails to start or shows errors.

**Quick Solutions**:

```bash
# 1. Run diagnostics
python insightvault.py diagnostics

# 2. Clean up ports and restart
python insightvault.py cleanup
python insightvault.py start

# 3. Use quick start (skips dependency installation)
python insightvault.py quick-start
```

## 🔍 Common Issues

### Python/Backend Issues

#### Module Not Found Errors

**Symptoms**: `ModuleNotFoundError: No module named '...'`

**Solutions**:

```bash
# 1. Ensure virtual environment is activated
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 2. Reinstall dependencies
pip install -r backend/requirements.txt

# 3. For Windows users, use Windows-specific requirements
pip install -r backend/requirements-windows.txt

# 4. Clear pip cache and reinstall
pip cache purge
pip install -r backend/requirements.txt
```

#### Port Already in Use

**Symptoms**: `Address already in use` or `Port 8000 is already in use`

**Solutions**:

```bash
# 1. Use the launcher to clean up ports
python insightvault.py cleanup

# 2. Manually kill processes (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 3. Manually kill processes (macOS/Linux)
lsof -ti:8000 | xargs kill -9

# 4. Use different ports
cd backend
uvicorn app.main:app --reload --port 8001
```

#### Unicode/Encoding Errors

**Symptoms**: `UnicodeEncodeError` or emoji-related errors

**Solutions**:

```bash
# 1. Set environment variable
# Windows:
set PYTHONIOENCODING=utf-8
# macOS/Linux:
export PYTHONIOENCODING=utf-8

# 2. Use the launcher (handles encoding automatically)
python insightvault.py start
```

### Node.js/Frontend Issues

#### npm Not Found

**Symptoms**: `'npm' is not recognized` or `npm: command not found`

**Solutions**:

```bash
# 1. Verify Node.js installation
node --version
npm --version

# 2. Reinstall Node.js and check "Add to PATH"
# Download from: https://nodejs.org/

# 3. Use the launcher (auto-fixes npm PATH on Windows)
python insightvault.py start

# 4. Manually add to PATH (Windows)
# Add C:\Program Files\nodejs\ to your PATH environment variable
```

#### Frontend Dependencies Fail to Install

**Symptoms**: `npm install` fails with errors

**Solutions**:

```bash
# 1. Clear npm cache
npm cache clean --force

# 2. Delete node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# 3. Use specific Node.js version
# Ensure you're using Node.js 16+ (recommended: 18+)

# 4. Check for network issues
npm config set registry https://registry.npmjs.org/
```

#### Frontend Server Won't Start

**Symptoms**: `npm run dev` fails or frontend not accessible

**Solutions**:

```bash
# 1. Check if port 3000 is available
# Windows:
netstat -ano | findstr :3000
# macOS/Linux:
lsof -i :3000

# 2. Use different port
cd frontend
npm run dev -- --port 3001

# 3. Check for build errors
npm run build

# 4. Clear Next.js cache
cd frontend
rm -rf .next
npm run dev
```

### API Key Issues

#### Invalid API Key

**Symptoms**: `Invalid API key` or authentication errors

**Solutions**:

```bash
# 1. Verify API key format
# Should start with 'sk-' and be 51 characters long

# 2. Check config.json
cat config.json
# Ensure the key is correct and not truncated

# 3. Test API key with OpenAI
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.openai.com/v1/models

# 4. Check OpenAI account status
# Visit: https://platform.openai.com/account/usage
```

#### API Rate Limits

**Symptoms**: `Rate limit exceeded` or slow responses

**Solutions**:

```bash
# 1. Check your OpenAI usage
# Visit: https://platform.openai.com/account/usage

# 2. Upgrade your OpenAI plan if needed
# Visit: https://platform.openai.com/account/billing

# 3. Use caching to reduce API calls
# Clear cache only when needed: Tools → Clear Cache
```

### Database Issues

#### Database Connection Errors

**Symptoms**: `Database connection failed` or SQL errors

**Solutions**:

```bash
# 1. Check database configuration
cat backend/.env
# Ensure DATABASE_URL is correct

# 2. For SQLite (development)
# Database file should be created automatically
# Check permissions on the backend/ directory

# 3. For PostgreSQL (production)
# Ensure PostgreSQL is running
# Check connection string format
```

#### Migration Errors

**Symptoms**: `Alembic` or database migration errors

**Solutions**:

```bash
# 1. Reset database (development only)
cd backend
rm -f *.db
# Restart the application

# 2. Run migrations manually
cd backend
alembic upgrade head

# 3. Check migration files
alembic history
```

### File Upload Issues

#### File Too Large

**Symptoms**: `File too large` or upload timeout

**Solutions**:

```bash
# 1. Check file size
# Large conversation files may need to be split

# 2. Increase upload limits
# Edit backend/app/main.py to increase max file size

# 3. Use chunked upload for large files
# The frontend supports chunked uploads automatically
```

#### Invalid File Format

**Symptoms**: `Invalid file format` or parsing errors

**Solutions**:

```bash
# 1. Ensure file is valid JSON
python -m json.tool conversations.json

# 2. Check file structure
# Should contain "conversations" array with message objects

# 3. Use sample data for testing
# Copy data/sample_conversations.json for testing
```

## 🔧 Advanced Troubleshooting

### System Diagnostics

Run comprehensive diagnostics:

```bash
python insightvault.py diagnostics
```

This will check:

- Python version and dependencies
- Node.js and npm availability
- Port availability
- File permissions
- Network connectivity

### Log Analysis

**Backend Logs**:

```bash
# Check backend logs
cd backend
uvicorn app.main:app --reload --log-level debug

# Check for specific errors
grep -i error backend/logs/*.log
```

**Frontend Logs**:

```bash
# Check browser console for errors
# Press F12 → Console tab

# Check Next.js logs
cd frontend
npm run dev
# Look for error messages in terminal
```

### Performance Issues

#### Slow Response Times

**Solutions**:

```bash
# 1. Check OpenAI API response times
# Test with: curl -w "@curl-format.txt" -o /dev/null -s "API_CALL"

# 2. Enable caching
# Ensure cache is enabled in settings

# 3. Optimize conversation processing
# Process conversations in smaller batches

# 4. Check system resources
# Monitor CPU, memory, and disk usage
```

#### Memory Issues

**Solutions**:

```bash
# 1. Clear cache
# Use the application's cache clearing feature

# 2. Restart services
python insightvault.py cleanup
python insightvault.py start

# 3. Check for memory leaks
# Monitor memory usage over time
```

## 🆘 Getting Help

### Before Opening an Issue

1. **Run Diagnostics**: `python insightvault.py diagnostics`
2. **Check Logs**: Look for error messages in terminal/browser
3. **Search Issues**: Check if your issue is already reported
4. **Try Quick Fixes**: Use the solutions above

### When Opening an Issue

Include the following information:

**System Information**:

- Operating System and version
- Python version: `python --version`
- Node.js version: `node --version`
- npm version: `npm --version`

**Error Details**:

- Complete error message
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

**Diagnostic Output**:

```bash
python insightvault.py diagnostics
```

### Issue Templates

Use these templates when opening issues:

**Bug Report**:

```
**Description**: Brief description of the issue

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**System Information**:
- OS: [e.g., Windows 10, macOS 12]
- Python: [e.g., 3.9.7]
- Node.js: [e.g., 18.12.0]

**Error Logs**:
[Paste error messages here]
```

**Feature Request**:

```
**Description**: Brief description of the feature

**Use Case**: Why this feature would be useful

**Proposed Solution**: How you think it should work

**Alternatives**: Any alternative solutions you've considered
```

## 📞 Support Channels

- **GitHub Issues**: [Report bugs and request features](https://github.com/your-username/InsightVault/issues)
- **GitHub Discussions**: [Ask questions and get help](https://github.com/your-username/InsightVault/discussions)
- **Documentation**: [Check the main docs](README.md) for more information

## 🔄 Recovery Procedures

### Complete Reset (Development)

If everything is broken and you need a fresh start:

```bash
# 1. Stop all services
python insightvault.py cleanup

# 2. Remove virtual environment
rm -rf venv

# 3. Remove node_modules
cd frontend
rm -rf node_modules package-lock.json
cd ..

# 4. Remove database
cd backend
rm -f *.db
cd ..

# 5. Reinstall everything
python insightvault.py start --auto-install
```

### Data Recovery

**Backup Important Data**:

```bash
# Backup your conversations
cp data/conversations.json backup/

# Backup your insights
cp output/* backup/

# Backup configuration
cp config.json backup/
```

**Restore from Backup**:

```bash
# Restore conversations
cp backup/conversations.json data/

# Restore insights
cp backup/* output/

# Restore configuration
cp backup/config.json .
```

---

_Still having issues? Open an issue on GitHub with the diagnostic output and we'll help you resolve it._
