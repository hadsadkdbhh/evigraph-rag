$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$autoFigureDir = "C:\Users\24431\Documents\AutoFigure-Edit"
$condaEnv = if ($env:AF_CONDA_ENV) { $env:AF_CONDA_ENV } else { "autofigure-edit" }

Write-Host "Repo: $repoRoot"
Write-Host "AutoFigure-Edit: $autoFigureDir"
Write-Host "Conda env: $condaEnv"

if (-not (Test-Path -LiteralPath $autoFigureDir)) {
    throw "AutoFigure-Edit source directory is missing."
}

$envList = conda env list | Out-String
if ($envList -notmatch "(^|\s)$([regex]::Escape($condaEnv))(\s|$)") {
    throw "Conda env '$condaEnv' is missing."
}

conda run -n $condaEnv python --version
conda run -n $condaEnv python -c "import fastapi, openai, PIL, torch, torchvision, transformers, cairosvg; print('core imports ok'); print('torch', torch.__version__)"
conda run -n $condaEnv python -m py_compile "$autoFigureDir\autofigure2.py" "$autoFigureDir\server.py"

$requiredFiles = @(
    "$repoRoot\paper\figures\evigraph_pipeline.png",
    "$repoRoot\paper\figures\autofigure_edit_main_figure_method.txt",
    "$repoRoot\paper\figures\references\F1.png",
    "$repoRoot\paper\figures\references\F2.png",
    "$repoRoot\paper\figures\references\1_res.png"
)
foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        throw "Missing required file: $file"
    }
}

$secrets = @(
    "AF_API_KEY",
    "AF_BASE_URL",
    "AF_PROVIDER",
    "AF_IMAGE_PROVIDER",
    "ROBOFLOW_API_KEY",
    "FAL_KEY",
    "AF_SAM_API_KEY"
)

foreach ($name in $secrets) {
    $value = [Environment]::GetEnvironmentVariable($name)
    if ([string]::IsNullOrWhiteSpace($value)) {
        Write-Host "$name=missing"
    } else {
        Write-Host "$name=set(length=$($value.Length))"
    }
}

Write-Host "Environment check complete."
