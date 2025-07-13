# InsightVault Development Commands for Windows/PowerShell
# Use these commands or their syntax as reference

# Backend Commands
Write-Host "=== Backend Commands ===" -ForegroundColor Green

# Start backend server
Write-Host "Start backend server:" -ForegroundColor Yellow
Write-Host "cd backend; python -m uvicorn app.main:app --reload" -ForegroundColor Cyan

# Install backend dependencies
Write-Host "Install backend dependencies:" -ForegroundColor Yellow
Write-Host "cd backend; pip install -r requirements.txt" -ForegroundColor Cyan

# Run database migrations
Write-Host "Run database migrations:" -ForegroundColor Yellow
Write-Host "cd backend; python -m alembic upgrade head" -ForegroundColor Cyan

# Run backend tests
Write-Host "Run backend tests:" -ForegroundColor Yellow
Write-Host "cd backend; python -m pytest" -ForegroundColor Cyan

# Frontend Commands
Write-Host "`n=== Frontend Commands ===" -ForegroundColor Green

# Install frontend dependencies
Write-Host "Install frontend dependencies:" -ForegroundColor Yellow
Write-Host "cd frontend; npm install" -ForegroundColor Cyan

# Start frontend development server
Write-Host "Start frontend development server:" -ForegroundColor Yellow
Write-Host "cd frontend; npm run dev" -ForegroundColor Cyan

# Run frontend tests
Write-Host "Run frontend tests:" -ForegroundColor Yellow
Write-Host "cd frontend; npm test" -ForegroundColor Cyan

# Combined Commands
Write-Host "`n=== Combined Commands ===" -ForegroundColor Green

# Start both servers
Write-Host "Start both servers (backend in background):" -ForegroundColor Yellow
Write-Host "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd backend; python -m uvicorn app.main:app --reload'" -ForegroundColor Cyan
Write-Host "cd frontend; npm run dev" -ForegroundColor Cyan

# Check project status
Write-Host "Check project status:" -ForegroundColor Yellow
Write-Host "dir" -ForegroundColor Cyan
Write-Host "cd backend; dir" -ForegroundColor Cyan
Write-Host "cd frontend; dir" -ForegroundColor Cyan

Write-Host "`n=== Environment Info ===" -ForegroundColor Green
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host "Python version: $(python --version)" -ForegroundColor Cyan
Write-Host "Node version: $(node --version)" -ForegroundColor Cyan
Write-Host "npm version: $(npm --version)" -ForegroundColor Cyan 