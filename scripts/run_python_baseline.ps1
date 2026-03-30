param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArgs
)

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$launcher = Join-Path $projectRoot "scripts\launchers\run_camera_cli.py"

if (-not (Test-Path $pythonExe)) {
    Write-Error "Expected project interpreter at '$pythonExe'. Run the repository bootstrap first."
    exit 1
}

if (-not (Test-Path $launcher)) {
    Write-Error "Expected CLI launcher at '$launcher'."
    exit 1
}

if (-not $CliArgs -or $CliArgs.Count -eq 0) {
    $CliArgs = @("--help")
}

Push-Location $projectRoot
try {
    & $pythonExe $launcher @CliArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
