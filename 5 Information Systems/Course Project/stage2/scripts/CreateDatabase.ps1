param(
    [string]$HostName = 'localhost', [int]$Port = 5432,
    [string]$DatabaseUser = 'postgres', [string]$DatabaseName = 'beauty_course',
    [switch]$WithDemoData, [string]$BackendRole
)
$ErrorActionPreference = 'Stop'
$stageRoot = Split-Path -Parent $PSScriptRoot
$psqlPath = (Get-Command psql.exe -ErrorAction Stop).Source
& $psqlPath -X -h $HostName -p $Port -U $DatabaseUser -d postgres -v ON_ERROR_STOP=1 -v "db_name=$DatabaseName" -f (Join-Path $stageRoot 'sql\00_create_database.sql')
if ($LASTEXITCODE -ne 0) { throw 'Database creation failed.' }
$demoFlag = if ($WithDemoData) { 'true' } else { 'false' }
& $psqlPath -X -h $HostName -p $Port -U $DatabaseUser -d $DatabaseName -v ON_ERROR_STOP=1 -v "with_demo_data=$demoFlag" -f (Join-Path $stageRoot 'sql\install.sql')
if ($LASTEXITCODE -ne 0) { throw 'Schema installation failed; the newly created database is preserved for inspection.' }
if ($BackendRole) {
    & $psqlPath -X -h $HostName -p $Port -U $DatabaseUser -d $DatabaseName -v ON_ERROR_STOP=1 -v "backend_role=$BackendRole" -f (Join-Path $stageRoot 'sql\06_grant_backend.sql')
    if ($LASTEXITCODE -ne 0) { throw 'Backend grants failed.' }
}
Write-Output "Installed database $DatabaseName."
