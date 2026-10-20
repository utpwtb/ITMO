param(
    [string]$HostName = 'localhost', [int]$Port = 5432,
    [string]$DatabaseUser = 'postgres', [string]$DatabaseName = 'beauty_course'
)
$ErrorActionPreference = 'Stop'
if ($DatabaseName -in @('postgres','template0','template1')) { throw 'System databases are not course-project targets.' }
$stageRoot = Split-Path -Parent $PSScriptRoot
$psqlPath = (Get-Command psql.exe -ErrorAction Stop).Source
& $psqlPath -X -h $HostName -p $Port -U $DatabaseUser -d postgres -v ON_ERROR_STOP=1 -v "db_name=$DatabaseName" -f (Join-Path $stageRoot 'sql\99_drop_database.sql')
if ($LASTEXITCODE -ne 0) { throw 'Database deletion failed. No other sessions are terminated by this script.' }
