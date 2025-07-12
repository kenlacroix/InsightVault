# Troubleshooting Guide

This guide covers common issues and their solutions when setting up and running InsightVault.

## 🚨 Common Issues

### Database Issues

#### "no such table: users" Error

**Problem**: After branch merges or fresh installations, you get database errors like:

```
sqlite3.OperationalError: no such table: users
```

**Cause**: The database file was reset or tables weren't created.

**Solution**:

```bash
# Run the database initialization script
cd backend
python init_db.py
```

**Prevention**: The application now automatically initializes the database on startup.

#### Database Connection Errors

**Problem**: Database connection failures or permission errors.

**Solution**:

1. Check if the database file exists: `ls backend/insightvault.db`
2. Ensure write permissions in the backend directory
3. Try deleting the database file and reinitializing:
   ```bash
   cd backend
   rm insightvault.db  # or del insightvault.db on Windows
   python init_db.py
   ```

### Backend Startup Issues

#### Port 8000 Already in Use

**Problem**: Multiple processes trying to use port 8000.

**Solution**:

```bash
# Windows - Find and kill processes
netstat -ano | findstr :8000
taskkill /F /PID <process_id>

# Linux/Mac - Find and kill processes
lsof -ti:8000 | xargs kill -9
```

#### Backend Crashes on Startup

**Problem**: Backend starts but crashes immediately.

**Common Causes**:

1. Missing dependencies
2. Database issues
3. Configuration problems

**Solution**:

1. Check the logs for specific error messages
2. Run the setup script: `python setup.py`
3. Verify all dependencies are installed
4. Check the configuration file

### Frontend Issues

#### "npm not found" Error

**Problem**: npm command not found on Windows.

**Solution**:

1. Install Node.js from https://nodejs.org/
2. Restart your terminal/command prompt
3. If still not working, try using the full path:
   ```bash
   "C:\Program Files\nodejs\npm.cmd" install
   ```

#### Frontend Build Errors

**Problem**: npm install or build fails.

**Solution**:

1. Clear npm cache: `npm cache clean --force`
2. Delete node_modules and reinstall:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### Dependency Issues

#### Rust Compilation Errors on Windows

**Problem**: Backend dependencies fail to install due to Rust compilation.

**Solution**:

1. Use minimal requirements: `pip install -r backend/requirements-minimal.txt`
2. Install Visual Studio Build Tools
3. Install Rust: https://rustup.rs/

#### Python Package Conflicts

**Problem**: Package version conflicts or installation failures.

**Solution**:

1. Use a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
2. Upgrade pip: `python -m pip install --upgrade pip`
3. Install packages individually if needed

### Configuration Issues

#### OpenAI API Key Not Working

**Problem**: AI features don't work or return errors.

**Solution**:

1. Verify your API key in `config.json`
2. Check if the key has sufficient credits
3. Ensure the key starts with `sk-`
4. Test the key manually:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        https://api.openai.com/v1/models
   ```

#### Missing Configuration File

**Problem**: Application can't find configuration.

**Solution**:

```bash
# Copy example configuration
cp config.json.example config.json
# Edit config.json with your settings
```

## 🔧 Diagnostic Commands

### System Health Check

```bash
# Run comprehensive diagnostics
python insightvault.py --diagnose
```

### Manual Service Testing

```bash
# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Check database
cd backend
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Port Availability

```bash
# Check if ports are available
netstat -an | grep :8000  # Windows
lsof -i :8000             # Linux/Mac
```

## 🆘 Getting Help

### Before Asking for Help

1. **Check the logs**: Look for specific error messages
2. **Run diagnostics**: Use `python insightvault.py --diagnose`
3. **Try the setup script**: `python setup.py`
4. **Check this guide**: Look for similar issues

### When Reporting Issues

Include the following information:

- Operating system and version
- Python version: `python --version`
- Node.js version: `node --version`
- Error messages and logs
- Steps to reproduce the issue

### Common Log Locations

- **Backend logs**: Check terminal output when running the backend
- **Frontend logs**: Check browser developer console
- **System logs**: Check system event logs for port conflicts

## 🔄 Reset and Recovery

### Complete Reset

If all else fails, you can reset everything:

```bash
# Stop all services
python insightvault.py --stop

# Clean up
rm -rf backend/insightvault.db
rm -rf frontend/node_modules
rm -rf frontend/.next

# Reinstall everything
python setup.py
```

### Data Backup

Before resetting, backup your data:

```bash
# Backup database
cp backend/insightvault.db backend/insightvault.db.backup

# Backup configuration
cp config.json config.json.backup
```

## 📞 Support

If you're still having issues:

1. Check the [GitHub Issues](https://github.com/your-username/InsightVault/issues)
2. Create a new issue with detailed information
3. Include system information and error logs
4. Describe what you've already tried
