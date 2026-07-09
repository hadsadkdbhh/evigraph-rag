param(
    [ValidateSet("regenerate", "import")]
    [string]$Mode = "regenerate",
    [string]$AutoFigureDir = "C:\Users\24431\Documents\AutoFigure-Edit",
    [string]$Python = $env:AF_PYTHON,
    [string]$CondaEnv = $env:AF_CONDA_ENV,
    [string]$Provider = $env:AF_PROVIDER,
    [string]$ApiKey = $env:AF_API_KEY,
    [string]$BaseUrl = $env:AF_BASE_URL,
    [string]$ImageProvider = $env:AF_IMAGE_PROVIDER,
    [string]$ImageApiKey = $env:AF_IMAGE_API_KEY,
    [string]$ImageBaseUrl = $env:AF_IMAGE_BASE_URL,
    [string]$ImageModel = $env:AF_IMAGE_MODEL,
    [string]$SvgModel = $env:AF_SVG_MODEL,
    [string]$SamBackend = $env:AF_SAM_BACKEND,
    [string]$SamApiKey = $env:AF_SAM_API_KEY,
    [string]$ReferenceImage = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($CondaEnv)) {
    $CondaEnv = "autofigure-edit"
}
$useConda = $false
if ([string]::IsNullOrWhiteSpace($Python)) {
    $condaCmd = Get-Command conda -ErrorAction SilentlyContinue
    if ($condaCmd) {
        $envList = conda env list | Out-String
        if ($envList -match "(^|\s)$([regex]::Escape($CondaEnv))(\s|$)") {
            $useConda = $true
        } else {
            $Python = "python"
        }
    } else {
        $Python = "python"
    }
}
if ([string]::IsNullOrWhiteSpace($Provider)) {
    $Provider = "custom"
}
if ([string]::IsNullOrWhiteSpace($SamBackend)) {
    $SamBackend = "roboflow"
}
if ([string]::IsNullOrWhiteSpace($SamApiKey)) {
    if ($SamBackend -eq "roboflow") {
        $SamApiKey = $env:ROBOFLOW_API_KEY
    } elseif ($SamBackend -eq "fal") {
        $SamApiKey = $env:FAL_KEY
    }
}
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    throw "Set AF_API_KEY first. Example: `$env:AF_API_KEY='your_key'"
}
if ($Provider -eq "custom" -and [string]::IsNullOrWhiteSpace($BaseUrl)) {
    throw "Provider custom requires AF_BASE_URL ending in /v1. Example: `$env:AF_BASE_URL='https://your-api.example/v1'"
}
if (($SamBackend -eq "roboflow" -or $SamBackend -eq "fal") -and [string]::IsNullOrWhiteSpace($SamApiKey)) {
    throw "SAM backend '$SamBackend' requires a key. Set ROBOFLOW_API_KEY, FAL_KEY, or AF_SAM_API_KEY."
}
if (-not (Test-Path -LiteralPath $AutoFigureDir)) {
    throw "AutoFigure-Edit directory not found: $AutoFigureDir"
}

$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$methodFile = Join-Path $repoRoot "paper\figures\autofigure_edit_main_figure_method.txt"
$inputFigure = Join-Path $repoRoot "paper\figures\evigraph_pipeline.png"
$outDir = Join-Path $repoRoot "outputs\autofigure_edit\main_figure_$Mode"
if ([string]::IsNullOrWhiteSpace($ReferenceImage)) {
    $ReferenceImage = Join-Path $repoRoot "paper\figures\references\F1.png"
}

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$args = @(
    (Join-Path $AutoFigureDir "autofigure2.py"),
    "--output_dir", $outDir,
    "--provider", $Provider,
    "--api_key", $ApiKey,
    "--sam_backend", $SamBackend,
    "--optimize_iterations", "0"
)

if (-not [string]::IsNullOrWhiteSpace($BaseUrl)) {
    $args += @("--base_url", $BaseUrl)
}
if (-not [string]::IsNullOrWhiteSpace($ImageProvider)) {
    $args += @("--image_provider", $ImageProvider)
}
if (-not [string]::IsNullOrWhiteSpace($ImageApiKey)) {
    $args += @("--image_api_key", $ImageApiKey)
}
if (-not [string]::IsNullOrWhiteSpace($ImageBaseUrl)) {
    $args += @("--image_base_url", $ImageBaseUrl)
}
if (-not [string]::IsNullOrWhiteSpace($ImageModel)) {
    $args += @("--image_model", $ImageModel)
}
if (-not [string]::IsNullOrWhiteSpace($SvgModel)) {
    $args += @("--svg_model", $SvgModel)
}
if (-not [string]::IsNullOrWhiteSpace($SamApiKey)) {
    $args += @("--sam_api_key", $SamApiKey)
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
    if ($useConda) {
        & conda run -n $CondaEnv python @args
    } else {
        & $Python @args
    }
    if ($LASTEXITCODE -ne 0) {
        throw "AutoFigure-Edit failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

Write-Host "AutoFigure-Edit output: $outDir"
Write-Host "Look for figure.png, samed.png, template.svg, optimized_template.svg, and final.svg in that folder."
