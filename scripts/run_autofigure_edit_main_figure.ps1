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

function Get-EnvValue {
    param([string]$Name)
    $value = [Environment]::GetEnvironmentVariable($Name, "Process")
    if ([string]::IsNullOrWhiteSpace($value)) {
        $value = [Environment]::GetEnvironmentVariable($Name, "User")
    }
    if ([string]::IsNullOrWhiteSpace($value)) {
        $value = [Environment]::GetEnvironmentVariable($Name, "Machine")
    }
    return $value
}

function Test-PlaceholderValue {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $false
    }
    return $Value -match "your|placeholder|example|api key|base url|compatible|python 3\.10|Python 3\.10|path|address"
}

function Test-NonAsciiValue {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $false
    }
    return $Value -match "[^\x00-\x7F]"
}

if ([string]::IsNullOrWhiteSpace($Python)) { $Python = Get-EnvValue "AF_PYTHON" }
if ([string]::IsNullOrWhiteSpace($CondaEnv)) { $CondaEnv = Get-EnvValue "AF_CONDA_ENV" }
if ([string]::IsNullOrWhiteSpace($Provider)) { $Provider = Get-EnvValue "AF_PROVIDER" }
if ([string]::IsNullOrWhiteSpace($ApiKey)) { $ApiKey = Get-EnvValue "AF_API_KEY" }
if ([string]::IsNullOrWhiteSpace($BaseUrl)) { $BaseUrl = Get-EnvValue "AF_BASE_URL" }
if ([string]::IsNullOrWhiteSpace($ImageProvider)) { $ImageProvider = Get-EnvValue "AF_IMAGE_PROVIDER" }
if ([string]::IsNullOrWhiteSpace($ImageApiKey)) { $ImageApiKey = Get-EnvValue "AF_IMAGE_API_KEY" }
if ([string]::IsNullOrWhiteSpace($ImageBaseUrl)) { $ImageBaseUrl = Get-EnvValue "AF_IMAGE_BASE_URL" }
if ([string]::IsNullOrWhiteSpace($ImageModel)) { $ImageModel = Get-EnvValue "AF_IMAGE_MODEL" }
if ([string]::IsNullOrWhiteSpace($SvgModel)) { $SvgModel = Get-EnvValue "AF_SVG_MODEL" }
if ([string]::IsNullOrWhiteSpace($SamBackend)) { $SamBackend = Get-EnvValue "AF_SAM_BACKEND" }
if ([string]::IsNullOrWhiteSpace($SamApiKey)) { $SamApiKey = Get-EnvValue "AF_SAM_API_KEY" }

if ([string]::IsNullOrWhiteSpace($CondaEnv)) {
    $CondaEnv = "autofigure-edit"
}
$useConda = $false
$condaEnvAvailable = $false
$condaCmd = Get-Command conda -ErrorAction SilentlyContinue
if ($condaCmd) {
    $envList = conda env list | Out-String
    if ($envList -match "(^|\s)$([regex]::Escape($CondaEnv))(\s|$)") {
        $condaEnvAvailable = $true
    }
}
if (Test-PlaceholderValue $Python) {
    Write-Host "Ignoring placeholder AF_PYTHON value and using conda env '$CondaEnv' when available."
    $Python = ""
}
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($condaEnvAvailable) {
        $useConda = $true
    } else {
        $Python = "python"
    }
} else {
    $pythonCommand = Get-Command $Python -ErrorAction SilentlyContinue
    $pythonPathExists = Test-Path -LiteralPath $Python
    if (-not $pythonCommand -and -not $pythonPathExists) {
        if ($condaEnvAvailable) {
            Write-Host "AF_PYTHON '$Python' is not executable; falling back to conda env '$CondaEnv'."
            $useConda = $true
        } else {
            throw "AF_PYTHON is set but not executable: $Python. Clear AF_PYTHON or set it to a real python.exe path."
        }
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
        $SamApiKey = Get-EnvValue "ROBOFLOW_API_KEY"
    } elseif ($SamBackend -eq "fal") {
        $SamApiKey = Get-EnvValue "FAL_KEY"
    }
}
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    throw "Set AF_API_KEY first. Example: `$env:AF_API_KEY='your_key'"
}
if ((Test-PlaceholderValue $ApiKey) -or (Test-NonAsciiValue $ApiKey)) {
    throw "AF_API_KEY still looks like placeholder text. Set it to the real model API key, not words like 'your API key'."
}
if ($Provider -eq "custom" -and [string]::IsNullOrWhiteSpace($BaseUrl)) {
    throw "Provider custom requires AF_BASE_URL ending in /v1. Example: `$env:AF_BASE_URL='https://your-api.example/v1'"
}
if ($Provider -eq "custom" -and ((Test-PlaceholderValue $BaseUrl) -or (Test-NonAsciiValue $BaseUrl))) {
    throw "AF_BASE_URL still looks like placeholder text. Set it to a real OpenAI-compatible /v1 URL, for example https://example.com/v1."
}
if ($Provider -eq "custom" -and $BaseUrl -notmatch "^https?://") {
    throw "AF_BASE_URL must start with http:// or https://."
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
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
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
