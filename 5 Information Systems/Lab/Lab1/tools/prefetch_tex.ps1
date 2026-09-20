$ErrorActionPreference = 'Stop'
$base = $PSScriptRoot
$entries = Get-Content (Join-Path $base 'tex-prefetch.json') -Raw | ConvertFrom-Json
$cache = Join-Path $base 'tex-ranges'
$entries | ForEach-Object -Parallel {
 $entry = $_
 $path = Join-Path $using:cache ($entry.start.ToString()+'-'+$entry.end.ToString())
 if (Test-Path -LiteralPath $path) { return }
 try {
  Invoke-WebRequest -Uri 'https://data1b.fullyjustified.net/tlextras-2022.0r0.tar' -Headers @{Range=('bytes='+$entry.start+'-'+$entry.end)} -OutFile ($path+'.part') -TimeoutSec 25
  if ((Get-Item -LiteralPath ($path+'.part')).Length -eq ($entry.end-$entry.start+1)) { Move-Item -LiteralPath ($path+'.part') -Destination $path -Force; Write-Output $entry.name }
 } catch { Write-Output ('Retry later: '+$entry.name) }
} -ThrottleLimit 8
