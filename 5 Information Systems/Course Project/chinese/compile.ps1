# Compile this translation using the existing project-local environment.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$engine = Join-Path $projectRoot '.tools\tectonic\tectonic.exe'
$previousCache = $env:TECTONIC_CACHE_DIR
$previousFontConfig = $env:FONTCONFIG_FILE
$env:TECTONIC_CACHE_DIR = Join-Path $projectRoot '.tools\tex-cache'
$env:FONTCONFIG_FILE = Join-Path $projectRoot '.tools\fonts.conf'
Push-Location $PSScriptRoot
try {
    & $engine --keep-logs --keep-intermediates 'stage1_report_zh.tex'
    if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $LASTEXITCODE" }
    Write-Output "PDF: $(Join-Path $PSScriptRoot 'stage1_report_zh.pdf')"
} finally {
    Pop-Location
    $env:TECTONIC_CACHE_DIR = $previousCache
    $env:FONTCONFIG_FILE = $previousFontConfig
}

