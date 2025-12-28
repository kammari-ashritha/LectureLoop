# PowerShell script to set Google API Key environment variable for LectureLoop

# Set the API key as an environment variable for the current session
$env:GOOGLE_API_KEY = "AIzaSyAO-lVQnVlh_Et-M4SlEI86wtnoSp6IS8s"

Write-Host "✅ Google API Key environment variable has been set for this PowerShell session." -ForegroundColor Green
Write-Host ""
Write-Host "Note: This environment variable will only last for this PowerShell session." -ForegroundColor Yellow
Write-Host "To make it permanent, you can:" -ForegroundColor Yellow
Write-Host "  1. Set it in System Environment Variables (Windows Settings)" -ForegroundColor Cyan
Write-Host "  2. Add it to your PowerShell profile" -ForegroundColor Cyan
Write-Host "  3. Create a .env file in the project root (recommended for development)" -ForegroundColor Cyan
Write-Host ""
Write-Host "To verify it's set, run: echo `$env:GOOGLE_API_KEY" -ForegroundColor Yellow

