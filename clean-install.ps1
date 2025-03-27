$ErrorActionPreference = "Stop"

# Set environment
$env:PYTHON = "C:\Users\USER\AppData\Local\Programs\Python\Python313\python.exe"
$env:GYP_MSVS_VERSION = "2022"

# Cleanup
Write-Host "Cleaning up..." -ForegroundColor Yellow
Stop-Process -Name node,python -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force node_modules, package-lock.json
npm cache clean --force

# Install
Write-Host "Installing..." -ForegroundColor Green
npm install --ignore-scripts
npm install --no-save --no-audit --production false --legacy-peer-deps
npm rebuild