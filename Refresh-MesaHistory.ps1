# Check if the mesa directory exists
if (-not (Test-Path "mesa")) {
    Write-Host "Mesa repository not found. Cloning..."
    git clone https://gitlab.freedesktop.org/mesa/mesa.git
}

# Enter the directory
Push-Location "mesa"

# Update the repository
Write-Host "Updating repository..."
git pull

# Generate the log
# Changed output file to match Python script (Mesa_Deep_Dive.txt)
$outFile = "..\Mesa_Deep_Dive.txt"
Write-Host "Generating log to $outFile..."
# Added encoding to utf8 to match Python expectation
git log --since="12 months ago" --pretty=format:"%ad | %s (%h)" --date=short | Out-File -FilePath $outFile -Encoding utf8

# Return to original directory
Pop-Location

Write-Host "Done! Searchable list created at $outFile"