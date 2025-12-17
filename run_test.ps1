# PowerShell script to run MVP test
# Usage: .\run_test.ps1 <zipcode>

param(
    [string]$zipcode = "75201"
)

Write-Host "=" -NoNewline
Write-Host ("=" * 59)
Write-Host "MVP Satellite Roof Damage Detection Test"
Write-Host "=" -NoNewline
Write-Host ("=" * 59)
Write-Host ""

# Activate venv if in parent directory
$venvPath = "..\AI_Roof_Damage_Detection\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..."
    & $venvPath
}

# Run the script
Write-Host "Running analysis for zipcode: $zipcode"
Write-Host "Recipient: aliyanew16@gmail.com"
Write-Host ""

python main.py $zipcode

