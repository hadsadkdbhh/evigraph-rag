param(
    [ValidateSet("regenerate", "import")]
    [string]$Mode = "regenerate",
    [string]$AutoFigureDir = "C:\Users\24431\Documents\AutoFigure-Edit",
    [string]$Python = $env:AF_PYTHON,
    [string]$Provider = $env:AF_PROVIDER,
    [string]$ApiKey = $env:AF_API_KEY,
    [string]$BaseUrl = $env:AF_BASE_URL,
    [string]$ImageModel = $env:AF_IMAGE_MODEL,
    [string]$SvgModel = $env:AF_SVG_MODEL,
    [string]$SamBackend = $env:AF_SAM_BACKEND,
    [string]$ReferenceImage = "C:\Users\24431\Documents\每日清单\paper\figures\references\F1.png"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Python)) {
    $Python = "python"
}
if ([string]::IsNullOrWhiteSpace($Provider)) {
    $Provider = "custom"
}
if ([string]::IsNullOrWhiteSpace($SamBackend)) {
    $SamBackend = "roboflow"
}
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    throw "Set AF_API_KEY first. Example: `$env:AF_API_KEY='your_key'"
}
if ($Provider -eq "custom" -and [string]::IsNullOrWhiteSpace($BaseUrl)) {
    throw "Provider custom requires AF_BASE_URL ending in /v1. Example: `$env:AF_BASE_URL='https://your-api.example/v1'"
}
if (-not (Test-Path -LiteralPath $AutoFigureDir)) {
    throw "AutoFigure-Edit directory not found: $AutoFigureDir"
}

$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$methodFile = Join-Path $repoRoot "paper\figures\autofigure_edit_main_figure_method.txt"
$inputFigure = Join-Path $repoRoot "paper\figures\evigraph_pipeline.png"
$outDir = Join-Path $repoRoot "outputs\autofigure_edit\main_figure_$Mode"

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$args = @(
    (Join-Path $AutoFigureDir "autofigure2.py"),
    "--output_dir", $outDir,
    "--provider", $Provider,
    "--api_key", $ApiKey,
    "--sam_backend", $SamBackend,
    "--optimize_iterations", "0"
)

if ($Provider -eq "custom") {
    $args += @("--base_url", $BaseUrl)
}
if (-not [string]::IsNullOrWhiteSpace($ImageModel)) {
    $args += @("--image_model", $ImageModel)
}
if (-not [string]::IsNullOrWhiteSpace($SvgModel)) {
    $args += @("--svg_model", $SvgModel)
}

if ($Mode -eq "regenerate") {
    if (-not (Test-Path -LiteralPath $ReferenceImage)) {
        throw "Reference image not found: $ReferenceImage"
    }
    $args += @(
        "--method_file", $methodFile,
        "--use_reference_image",
        "--reference_image_path", $ReferenceImage
    )
} else {
    $args += @(
        "--input_figure_path", $inputFigure
    )
}

Push-Location $AutoFigureDir
try {
    & $Python @args
    if ($LASTEXITCODE -ne 0) {
        throw "AutoFigure-Edit failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

Write-Host "AutoFigure-Edit output: $outDir"
Write-Host "Look for figure.png, samed.png, template.svg, optimized_template.svg, and final.svg in that folder."
