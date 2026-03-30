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

$installSpec = "-e ."
$installProfile = "core"
if ($IncludeOpenCv) {
    $installSpec = "-e .[opencv]"
    $installProfile = "core + OpenCV"
} elseif ($Dev) {
    $installSpec = "-e ."
    $installProfile = "developer baseline"
}

Invoke-Step "Installing project with $installSpec" {
    & $pipExe install $installSpec
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
Write-Host "Installed profile: $installProfile"
if ($VmbPyWheel) {
    Write-Host "Installed VmbPy wheel: $VmbPyWheel"
} else {
    Write-Host "VmbPy wheel: not installed by bootstrap"
    Write-Host "Hardware guardrail: real-camera commands still require a local Vimba X SDK install and a VmbPy wheel in this .venv."
}
if (-not $IncludeOpenCv) {
    Write-Host "OpenCV extra: not installed; preview/save helpers that require OpenCV remain unavailable."
}
Write-Host "Preferred package entry point: $pythonExe -m vision_platform.apps.camera_cli"
Write-Host "Installed console entry point after editable install: vision-platform-cli"
Write-Host "Preferred local helper: .\\scripts\\run_python_baseline.ps1"
