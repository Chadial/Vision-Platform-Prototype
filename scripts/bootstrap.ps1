param(
    [switch]$IncludeOpenCv,
    [switch]$Dev,
    [string]$Python = "py -3.11",
    [switch]$RecreateVenv,
    [string]$VmbPyWheel
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

function Invoke-Step {
    param(
        [string]$Message,
        [scriptblock]$Action
    )

    Write-Host "==> $Message"
    & $Action
}

if ($RecreateVenv -and (Test-Path $venvPath)) {
    Write-Host "==> Removing existing virtual environment at $venvPath"
    Remove-Item -Recurse -Force $venvPath
}

if (-not (Test-Path $pythonExe)) {
    Invoke-Step "Creating virtual environment" {
        Invoke-Expression "$Python -m venv `"$venvPath`""
    }
}

Invoke-Step "Upgrading pip" {
    & $pythonExe -m pip install --upgrade pip
}

$requirementsFile = "requirements.txt"
if ($IncludeOpenCv) {
    $requirementsFile = "requirements-opencv.txt"
} elseif ($Dev) {
    $requirementsFile = "requirements-dev.txt"
}

Invoke-Step "Installing dependencies from $requirementsFile" {
    & $pipExe install -r (Join-Path $projectRoot $requirementsFile)
}

if ($VmbPyWheel) {
    if (-not (Test-Path $VmbPyWheel)) {
        throw "The specified VmbPy wheel does not exist: $VmbPyWheel"
    }

    Invoke-Step "Installing VmbPy from local wheel" {
        & $pipExe install $VmbPyWheel
    }
}

Write-Host ""
Write-Host "Bootstrap completed."
Write-Host "Virtual environment: $venvPath"
Write-Host "Python executable: $pythonExe"
if ($IncludeOpenCv) {
    Write-Host "Installed profile: core + OpenCV"
} elseif ($Dev) {
    Write-Host "Installed profile: developer baseline"
} else {
    Write-Host "Installed profile: core"
}
if ($VmbPyWheel) {
    Write-Host "Installed VmbPy wheel: $VmbPyWheel"
} else {
    Write-Host "VmbPy wheel: not installed by bootstrap"
}
