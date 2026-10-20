$ErrorActionPreference = 'Stop'
$stageRoot = Split-Path -Parent $PSScriptRoot
$projectRoot = Split-Path -Parent $stageRoot
$engine = Join-Path $projectRoot '.tools\tectonic\tectonic.exe'
$outDir = Join-Path $stageRoot 'output\pdf'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$oldCache = $env:TECTONIC_CACHE_DIR
$oldFonts = $env:FONTCONFIG_FILE
$env:TECTONIC_CACHE_DIR = Join-Path $projectRoot '.tools\tex-cache'
$env:FONTCONFIG_FILE = Join-Path $projectRoot '.tools\fonts.conf'
try {
    & $engine --keep-logs --keep-intermediates --outdir $outDir (Join-Path $stageRoot 'report\stage2_report.tex')
    if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $LASTEXITCODE" }
    Write-Output (Join-Path $outDir 'stage2_report.pdf')
} finally {
    $env:TECTONIC_CACHE_DIR = $oldCache
    $env:FONTCONFIG_FILE = $oldFonts
}
