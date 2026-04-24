# Stop any existing processes on ports 5000 and 5001 (optional but helpful)
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Id (Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "--- Starting Bus Tracking System ---" -ForegroundColor Cyan

# 1. Start Backend (Port 5001)
Write-Host "Launching Backend (Port 5001)..." -ForegroundColor Yellow
Start-Process python -ArgumentList "app.py" -WorkingDirectory "..\bus_backend1" -NoNewWindow

# 2. Start Frontend/Middleware (Port 5000)
Write-Host "Launching Frontend (Port 5000)..." -ForegroundColor Yellow
Start-Process python -ArgumentList "app.py" -WorkingDirectory ".\college_project" -NoNewWindow

Write-Host "System is starting up. Please wait a few seconds..." -ForegroundColor Green
Write-Host "Frontend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:5001/api/buses" -ForegroundColor Cyan
