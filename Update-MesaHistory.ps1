# Configuration
$repoPath = ".\mesa"
$changelogHistoryFile = ".\Mesa_Changelog_History.txt"
$summariesFile = ".\Mesa_Summaries.txt"

# 1. Update Repository
if (Test-Path $repoPath) {
    Write-Host "Updating Mesa repository..."
    Push-Location $repoPath
    git pull
    Pop-Location
} else {
    Write-Host "Error: Mesa directory not found. Please run 'git clone https://gitlab.freedesktop.org/mesa/mesa.git' first."
    exit
}

# 2. Generate Changelog History Log (Raw Git History)
Write-Host "Generating Changelog History Log (Last 12 Months)..."
# Uses git log to capture everything, formatted as: YYYY-MM-DD | Message (Hash)
git -C $repoPath log --since="12 months ago" --pretty=format:"%ad | %s (%h)" --date=short | Out-File -FilePath $changelogHistoryFile -Encoding utf8

# 3. Generate Summaries (Compiled Release Notes)
Write-Host "Compiling Release Notes (Top 50 newest)..."

# Find .rst files that look like version numbers (e.g., 24.0.1.rst), sort them by version (newest first)
$relNotes = Get-ChildItem "$repoPath\docs\relnotes\*.rst" |
    Where-Object { $_.BaseName -match "^\d+\.\d+(\.\d+)?$" } |
    Sort-Object { [version]$_.BaseName } -Descending |
    Select-Object -First 50

# Create the summary file
"MESA RELEASE NOTES COMPILATION (Generated $(Get-Date))" | Out-File -FilePath $summariesFile -Encoding utf8
"Includes the 50 most recent releases." | Out-File -FilePath $summariesFile -Append -Encoding utf8
"--------------------------------------------------" | Out-File -FilePath $summariesFile -Append -Encoding utf8

foreach ($file in $relNotes) {
    Write-Host "Processing $($file.BaseName)..."

    # Add a visual separator for each version
    "`r`n`r`n==================================================" | Out-File -FilePath $summariesFile -Append -Encoding utf8
    " RELEASE: $($file.BaseName)" | Out-File -FilePath $summariesFile -Append -Encoding utf8
    "==================================================`r`n" | Out-File -FilePath $summariesFile -Append -Encoding utf8

    # Append the content of the release note
    Get-Content $file.FullName | Out-File -FilePath $summariesFile -Append -Encoding utf8
}

Write-Host "--------------------------------------------------"
Write-Host "Done!"
Write-Host "   1. Raw History:    $changelogHistoryFile"
Write-Host "   2. Release Notes:  $summariesFile"
