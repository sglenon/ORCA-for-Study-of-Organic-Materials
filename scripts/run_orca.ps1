param(
    [Parameter(Mandatory=$true)][string]$InputFile,
    [string]$OutputFile
)
if (-not $env:ORCA_EXE) { throw "Set ORCA_EXE to the full path of orca.exe" }
if (-not $OutputFile) { $OutputFile = [System.IO.Path]::ChangeExtension($InputFile, ".out") }
$workdir = Split-Path -Parent (Resolve-Path $InputFile)
$inputName = Split-Path -Leaf $InputFile
$outputName = Split-Path -Leaf $OutputFile
Push-Location $workdir
try {
    & $env:ORCA_EXE $inputName *> $outputName
    if (-not (Select-String -Path $outputName -Pattern "ORCA TERMINATED NORMALLY" -Quiet)) {
        throw "ORCA did not terminate normally. Inspect $OutputFile"
    }
} finally { Pop-Location }
Write-Host "Completed: $OutputFile"
