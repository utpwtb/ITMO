param(
 [string]$PostgresBin = 'C:\Program Files\PostgreSQL\17\bin',
 [int]$DatabasePort = 55441,
 [int]$HttpPort = 18081
)
$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot -Parent
$runtime = Join-Path $project '.runtime'
New-Item -ItemType Directory -Force $runtime | Out-Null
$data = Join-Path $runtime 'pgdata'
$repo = Join-Path $runtime 'm2'
$settings = Join-Path $runtime 'settings.xml'
'<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0"><mirrors><mirror><id>central</id><mirrorOf>*</mirrorOf><url>https://repo.maven.apache.org/maven2</url></mirror></mirrors></settings>' | Set-Content -LiteralPath $settings
if (!(Test-Path (Join-Path $data 'PG_VERSION'))) {
 & (Join-Path $PostgresBin 'initdb.exe') -D $data -U movie_lab -A trust --encoding=UTF8 --locale=C
 if ($LASTEXITCODE -ne 0) { throw 'initdb failed' }
}
& (Join-Path $PostgresBin 'pg_ctl.exe') -D $data status | Out-Null
if ($LASTEXITCODE -ne 0) {
 & (Join-Path $PostgresBin 'pg_ctl.exe') -D $data -l (Join-Path $runtime 'postgres.log') -o "-h 127.0.0.1 -p $DatabasePort" start
 if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL startup failed; check that the port is free.' }
}
foreach ($db in @('movie_lab','movie_lab_test')) {
 $exists = & (Join-Path $PostgresBin 'psql.exe') -h 127.0.0.1 -p $DatabasePort -U movie_lab -d postgres -Atc "SELECT 1 FROM pg_database WHERE datname='$db'"
 if ($exists -ne '1') { & (Join-Path $PostgresBin 'createdb.exe') -h 127.0.0.1 -p $DatabasePort -U movie_lab $db; if($LASTEXITCODE -ne 0){throw 'createdb failed'} }
}
$initialized = & (Join-Path $PostgresBin 'psql.exe') -h 127.0.0.1 -p $DatabasePort -U movie_lab -d movie_lab -Atc "SELECT to_regclass('public.movie') IS NOT NULL"
if ($initialized -ne 't') {
 & (Join-Path $PostgresBin 'psql.exe') -h 127.0.0.1 -p $DatabasePort -U movie_lab -d movie_lab -v ON_ERROR_STOP=1 -f (Join-Path $project 'database/schema.sql')
 if($LASTEXITCODE -ne 0){throw 'Schema initialization failed'}
}
Push-Location $project
try {
 & mvn -B -s $settings -gs $settings "-Dmaven.repo.local=$repo" "-DMOVIE_TEST_DB_URL=jdbc:postgresql://127.0.0.1:$DatabasePort/movie_lab_test" verify
 if($LASTEXITCODE -ne 0){throw 'Build/tests failed'}
 & mvn -B -s $settings -gs $settings "-Dmaven.repo.local=$repo" dependency:get '-Dartifact=fish.payara.extras:payara-micro:6.2025.1' '-Dtransitive=false'
 if($LASTEXITCODE -ne 0){throw 'Payara download failed'}
 $jar = Join-Path $repo 'fish/payara/extras/payara-micro/6.2025.1/payara-micro-6.2025.1.jar'
 Write-Host "Open http://localhost:$HttpPort/movie-lab/ ; local login: student / student (unless environment variables override it)"
 & java "-DMOVIE_DB_URL=jdbc:postgresql://127.0.0.1:$DatabasePort/movie_lab" -jar $jar --deploy (Join-Path $project 'target/movie-lab.war') --port $HttpPort --noCluster --rootdir (Join-Path $runtime 'payara')
} finally { Pop-Location }
