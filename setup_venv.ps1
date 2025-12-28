# PowerShell script to set up virtual environment for LectureLoop

Write-Host "Creating virtual environment for LectureLoop..." -ForegroundColor Green
python -m venv venv

Write-Host ""
Write-Host "Virtual environment created!" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment, run:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then install requirements with:" -ForegroundColor Yellow
Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan


