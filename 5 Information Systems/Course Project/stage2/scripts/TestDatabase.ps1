param([string]$PythonPath)
$ErrorActionPreference = 'Stop'
if (-not $PythonPath) {
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    $PythonPath = if (Test-Path -LiteralPath $bundledPython) { $bundledPython } else { (Get-Command python.exe -ErrorAction Stop).Source }
}
$stageRoot = Split-Path -Parent $PSScriptRoot
& $PythonPath (Join-Path $stageRoot 'tests\run_all.py')
if ($LASTEXITCODE -ne 0) { throw 'Database verification failed. See verification/test_results.json.' }
