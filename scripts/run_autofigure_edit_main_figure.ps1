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
    [string]$ImageSize = $env:AF_IMAGE_SIZE,
    [switch]$DisableAutoUpscale,
    [string]$SamPrompt = $env:AF_SAM_PROMPT,
    [string]$MinScore = $env:AF_MIN_SCORE,
    [string]$SamBackend = $env:AF_SAM_BACKEND,
    [string]$SamApiKey = $env:AF_SAM_API_KEY,
    [string]$ReferenceImage = "",
    [switch]$NoIconReplacement
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
if ([string]::IsNullOrWhiteSpace($ImageSize)) { $ImageSize = Get-EnvValue "AF_IMAGE_SIZE" }
if ([string]::IsNullOrWhiteSpace($SamPrompt)) { $SamPrompt = Get-EnvValue "AF_SAM_PROMPT" }
if ([string]::IsNullOrWhiteSpace($MinScore)) { $MinScore = Get-EnvValue "AF_MIN_SCORE" }
if ([string]::IsNullOrWhiteSpace($SamBackend)) { $SamBackend = Get-EnvValue "AF_SAM_BACKEND" }
if ([string]::IsNullOrWhiteSpace($SamApiKey)) { $SamApiKey = Get-EnvValue "AF_SAM_API_KEY" }

if ([string]::IsNullOrWhiteSpace($CondaEnv)) {
    $CondaEnv = "autofigure-edit"
}
$useConda = $false
$condaEnvAvailable = $false
$condaPython = $null
$condaCmd = Get-Command conda -ErrorAction SilentlyContinue
if ($condaCmd) {
    try {
        $envJson = conda env list --json | ConvertFrom-Json
        foreach ($envPath in $envJson.envs) {
            if ((Split-Path $envPath -Leaf) -eq $CondaEnv) {
                $candidatePython = Join-Path $envPath "python.exe"
                if (Test-Path -LiteralPath $candidatePython) {
                    $condaEnvAvailable = $true
                    $condaPython = $candidatePython
                }
                break
            }
        }
    } catch {
        $envList = conda env list | Out-String
        if ($envList -match "(^|\s)$([regex]::Escape($CondaEnv))(\s|$)") {
            $condaEnvAvailable = $true
        }
    }
}
if (Test-PlaceholderValue $Python) {
    Write-Host "Ignoring placeholder AF_PYTHON value and using conda env '$CondaEnv' when available."
    $Python = ""
}
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($condaEnvAvailable -and -not [string]::IsNullOrWhiteSpace($condaPython)) {
        $Python = $condaPython
    } elseif ($condaEnvAvailable) {
        $useConda = $true
    } else {
        $Python = "python"
    }
} else {
    $pythonCommand = Get-Command $Python -ErrorAction SilentlyContinue
    $pythonPathExists = Test-Path -LiteralPath $Python
    if (-not $pythonCommand -and -not $pythonPathExists) {
        if ($condaEnvAvailable -and -not [string]::IsNullOrWhiteSpace($condaPython)) {
            Write-Host "AF_PYTHON '$Python' is not executable; falling back to conda env python '$condaPython'."
            $Python = $condaPython
        } elseif ($condaEnvAvailable) {
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
if ([string]::IsNullOrWhiteSpace($SamPrompt)) {
    $SamPrompt = "icon,robot,animal,person"
}
if ([string]::IsNullOrWhiteSpace($MinScore)) {
    $MinScore = "0.0"
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
if ($Provider -eq "custom" -and $BaseUrl -match "teio\.me") {
    if ([string]::IsNullOrWhiteSpace($ImageProvider)) {
        $ImageProvider = "openai"
    }
    if ([string]::IsNullOrWhiteSpace($ImageBaseUrl)) {
        $ImageBaseUrl = $BaseUrl
    }
    if ([string]::IsNullOrWhiteSpace($ImageApiKey)) {
        $ImageApiKey = $ApiKey
    }
    if ([string]::IsNullOrWhiteSpace($ImageModel)) {
        $ImageModel = "gpt-image-2"
    }
    if ([string]::IsNullOrWhiteSpace($SvgModel)) {
        $SvgModel = "gpt-5.4"
    }
    if ([string]::IsNullOrWhiteSpace($ImageSize)) {
        $ImageSize = "1K"
    }
    Write-Host "Detected teio.me custom provider; using image model '$ImageModel' and SVG model '$SvgModel'."
}
if ($NoIconReplacement) {
    $MinScore = "1.01"
    Write-Host "NoIconReplacement enabled; SAM boxes will be suppressed to skip RMBG icon extraction."
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
if (-not [string]::IsNullOrWhiteSpace($ImageSize)) {
    $args += @("--image_size", $ImageSize)
}
if ($DisableAutoUpscale -or ($Provider -eq "custom" -and $BaseUrl -match "teio\.me")) {
    $args += @("--disable_auto_upscale")
}
if (-not [string]::IsNullOrWhiteSpace($SamPrompt)) {
    $args += @("--sam_prompt", $SamPrompt)
}
if (-not [string]::IsNullOrWhiteSpace($MinScore)) {
    $args += @("--min_score", $MinScore)
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
    if (-not $NoIconReplacement -and [string]::IsNullOrWhiteSpace((Get-EnvValue "HF_TOKEN"))) {
        Write-Host "HF_TOKEN is not set; enabling NoIconReplacement for import mode to avoid RMBG-2.0 gated-model failure."
        $args += @("--min_score", "1.01")
    }
    $args += @(
        "--input_figure_path", $inputFigure
    )
}

Push-Location $AutoFigureDir
try {
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUNBUFFERED = "1"
    $rawOutPath = Join-Path $outDir "autofigure_run.raw.out.log"
    $rawErrPath = Join-Path $outDir "autofigure_run.raw.err.log"
    $logPath = Join-Path $outDir "autofigure_run.log"
    Write-Host "AutoFigure-Edit log: $logPath"
    if ($useConda) {
        $process = Start-Process -FilePath "conda" -ArgumentList (@("run", "-n", $CondaEnv, "python") + $args) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $rawOutPath -RedirectStandardError $rawErrPath
    } else {
        $process = Start-Process -FilePath $Python -ArgumentList $args -NoNewWindow -Wait -PassThru -RedirectStandardOutput $rawOutPath -RedirectStandardError $rawErrPath
    }
    $exitCode = $process.ExitCode
    $logText = ""
    $rawPieces = @()
    if (Test-Path -LiteralPath $rawOutPath) {
        $rawPieces += Get-Content -LiteralPath $rawOutPath -Raw -ErrorAction SilentlyContinue
    }
    if (Test-Path -LiteralPath $rawErrPath) {
        $rawPieces += Get-Content -LiteralPath $rawErrPath -Raw -ErrorAction SilentlyContinue
    }
    $logText = ($rawPieces -join "`n")
    if (-not [string]::IsNullOrWhiteSpace($logText)) {
        if (-not [string]::IsNullOrWhiteSpace($ApiKey)) {
            $logText = $logText -replace [regex]::Escape($ApiKey), "[AF_API_KEY]"
        }
        if (-not [string]::IsNullOrWhiteSpace($ImageApiKey)) {
            $logText = $logText -replace [regex]::Escape($ImageApiKey), "[AF_IMAGE_API_KEY]"
        }
        if (-not [string]::IsNullOrWhiteSpace($SamApiKey)) {
            $logText = $logText -replace [regex]::Escape($SamApiKey), "[AF_SAM_API_KEY]"
        }
        $logText = $logText -replace 'sk-[A-Za-z0-9_-]{20,}', '[AF_API_KEY]'
        $logText = $logText -replace '(--api_key\s+)\S+', '$1[AF_API_KEY]'
        $logText = $logText -replace '(--sam_api_key\s+)\S+', '$1[AF_SAM_API_KEY]'
        Set-Content -LiteralPath $logPath -Value $logText -Encoding utf8
        Remove-Item -LiteralPath $rawOutPath -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $rawErrPath -Force -ErrorAction SilentlyContinue
    }
    if (-not [string]::IsNullOrWhiteSpace($logText)) {
        $tail = ($logText -split "`r?`n") | Select-Object -Last 30
        $tail | ForEach-Object { Write-Host $_ }
    }
    if ($exitCode -ne 0) {
        throw "AutoFigure-Edit failed with exit code $exitCode. See sanitized log: $logPath"
    }
} finally {
    Pop-Location
}

Write-Host "AutoFigure-Edit output: $outDir"
Write-Host "Look for figure.png, samed.png, template.svg, optimized_template.svg, and final.svg in that folder."
