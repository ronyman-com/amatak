# PowerShell script to build the Windows installer
$ErrorActionPreference = "Stop"

# Check requirements
if (-not (Test-Path "makensis.exe")) {
    Write-Host "Downloading NSIS..."
    Invoke-WebRequest "https://nsis.sourceforge.io/mediawiki/images/4/4a/Nsis-3.09.zip" -OutFile "nsis.zip"
    Expand-Archive "nsis.zip" -DestinationPath ".\nsis"
    $env:PATH += ";.\nsis\NSIS\Bin"
}

# Create distribution
python -m pip install pyinstaller
pyinstaller .\bin\amatak.py --onefile --distpath .\dist\windows\bin
pyinstaller .\bin\amatakd.py --onefile --distpath .\dist\windows\bin
pyinstaller .\bin\akc.py --onefile --distpath .\dist\windows\bin

# Copy runtime files
Copy-Item -Path ".\amatak" -Destination ".\dist\windows\amatak" -Recurse
Copy-Item -Path ".\stdlib" -Destination ".\dist\windows\stdlib" -Recurse
Copy-Item -Path ".\examples" -Destination ".\dist\windows\examples" -Recurse
Copy-Item -Path ".\docs" -Destination ".\dist\windows\docs" -Recurse

# Build installer
makensis .\installer\windows\amatak.nsi

Write-Host "Installer created at .\Amatak-Installer.exe"