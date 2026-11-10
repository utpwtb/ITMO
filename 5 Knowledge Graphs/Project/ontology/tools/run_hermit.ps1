param(
    [string]$ProtegeDirectory = 'C:\develop\Protege-5.6.9',
    [string]$JdkDirectory = 'C:\Program Files\Java\jdk-17'
)
$ErrorActionPreference = 'Stop'
$ontologyRoot = Split-Path -Parent $PSScriptRoot
$dependencyDirectory = Join-Path $PSScriptRoot 'hermit-libs'
New-Item -ItemType Directory -Force -Path $dependencyDirectory | Out-Null
# OSGi embeds these dependencies in HermiT. Extract copies locally for the standalone JVM.
Add-Type -AssemblyName System.IO.Compression.FileSystem
$hermitJar = Join-Path $ProtegeDirectory 'plugins\org.semanticweb.hermit-1.4.3.456.jar'
$dependencyJars = @($hermitJar, (Join-Path $ProtegeDirectory 'bundles\owlapi-osgidistribution.jar'))
foreach ($dependencyJar in $dependencyJars) {
    $archive = [IO.Compression.ZipFile]::OpenRead($dependencyJar)
    try {
        foreach ($entry in $archive.Entries) {
            if ($entry.FullName -match '\.jar$') {
                [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, (Join-Path $dependencyDirectory $entry.Name), $true)
            }
        }
    } finally { $archive.Dispose() }
}
$classpath = "$ProtegeDirectory\bundles\*;$hermitJar;$dependencyDirectory\*"
foreach ($variant in @('demo','full')) {
    & "$JdkDirectory\bin\java.exe" '-Dfile.encoding=UTF-8' "-Dlogback.configurationFile=$PSScriptRoot\logback.xml" '-Xmx2G' '--class-path' $classpath `
        (Join-Path $PSScriptRoot 'VerifyOntology.java') `
        (Join-Path $ontologyRoot "output\ontologies\lol_$variant.owl") (Join-Path $ontologyRoot 'output')
    if ($LASTEXITCODE -ne 0) { throw "HermiT validation failed for $variant" }
}
