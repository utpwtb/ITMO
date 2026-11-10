param(
    [string]$PythonExecutable = 'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1030-493-0_26.1030.493.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe'
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $PythonExecutable)) {
    throw 'Pass -PythonExecutable with a working Python 3.12+ interpreter that has requirements.txt installed.'
}
$auditScript = Join-Path $PSScriptRoot 'audit_lab4.py'
$auditArtifacts = Join-Path $PSScriptRoot 'artifacts'
New-Item -ItemType Directory -Path $auditArtifacts -Force | Out-Null
& $PythonExecutable -X utf8 -B $auditScript 2>&1 | Tee-Object -FilePath (Join-Path $auditArtifacts 'run.log')
exit $LASTEXITCODE
