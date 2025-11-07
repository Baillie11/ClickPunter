# ClickPunter - Git Setup Script
# This script initializes the git repository and prepares for GitHub

Write-Host "🏇 ClickPunter - Git Setup" -ForegroundColor Green
Write-Host ""

# Check if git is installed
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/win"
    exit 1
}

# Initialize git repository
Write-Host "📦 Initializing git repository..." -ForegroundColor Yellow
git init

# Add all files
Write-Host "➕ Adding all files..." -ForegroundColor Yellow
git add .

# Create first commit
Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: ClickPunter - ABC Method Horse Racing Assistant"

Write-Host ""
Write-Host "✅ Git repository initialized successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://github.com/new to create a new repository"
Write-Host "2. Repository name: ClickPunter"
Write-Host "3. Description: Horse racing betting strategy app using the ABC Method"
Write-Host "4. Choose public or private"
Write-Host "5. Don't initialize with README (we already have one)"
Write-Host ""
Write-Host "6. After creating on GitHub, run these commands:" -ForegroundColor Cyan
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/ClickPunter.git"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
Write-Host ""
Write-Host "🎉 Done!" -ForegroundColor Green
