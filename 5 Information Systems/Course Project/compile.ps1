# Compile the existing multi-file report with the project-local XeTeX engine.
$ErrorActionPreference = 'Stop'
$engine = Join-Path $PSScriptRoot '.tools\tectonic\tectonic.exe'
if (-not (Test-Path -LiteralPath $engine)) {
    throw 'Project-local Tectonic is missing from .tools\tectonic.'
}
$previousCache = $env:TECTONIC_CACHE_DIR
$previousFontConfig = $env:FONTCONFIG_FILE
$env:TECTONIC_CACHE_DIR = Join-Path $PSScriptRoot '.tools\tex-cache'
New-Item -ItemType Directory -Force -Path $env:TECTONIC_CACHE_DIR | Out-Null
$fontCache = Join-Path $PSScriptRoot '.tools\font-cache'
New-Item -ItemType Directory -Force -Path $fontCache | Out-Null
$fontDirectoryXml = [System.Security.SecurityElement]::Escape((Join-Path $env:WINDIR 'Fonts').Replace('\', '/'))
$fontCacheXml = [System.Security.SecurityElement]::Escape($fontCache.Replace('\', '/'))
$env:FONTCONFIG_FILE = Join-Path $PSScriptRoot '.tools\fonts.conf'
[System.IO.File]::WriteAllText($env:FONTCONFIG_FILE,
    "<?xml version='1.0'?><fontconfig><dir>$fontDirectoryXml</dir><cachedir>$fontCacheXml</cachedir></fontconfig>",
    [System.Text.UTF8Encoding]::new($false))
Push-Location $PSScriptRoot
try {
    & $engine --keep-logs --keep-intermediates 'stage1_report.tex'
    if ($LASTEXITCODE -ne 0) { throw "LaTeX compilation failed (exit $LASTEXITCODE)." }
    Write-Output "PDF: $(Join-Path $PSScriptRoot 'stage1_report.pdf')"
}
finally {
    Pop-Location
    $env:TECTONIC_CACHE_DIR = $previousCache
    $env:FONTCONFIG_FILE = $previousFontConfig
}
