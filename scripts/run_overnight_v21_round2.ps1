param(
    [switch]$SkipNeural
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $Root

$LogDir = Join-Path $Root "outputs\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TranscriptPath = Join-Path $LogDir "overnight_v21_round2_$Stamp.log"

Start-Transcript -Path $TranscriptPath | Out-Null

try {
    Write-Host "[overnight-round2] root: $Root"
    Write-Host "[overnight-round2] transcript: $TranscriptPath"

    $manifests = @(
        ".\configs\experiments.finqa_600.local_planner_strong_retrieval_baselines_v21.json"
    )

    if (-not $SkipNeural) {
        $manifests += ".\configs\experiments.finqa_600.neural_retrieval_baselines_v21.json"
    }

    foreach ($manifest in $manifests) {
        Write-Host ""
        Write-Host "[overnight-round2] running $manifest"
        python .\scripts\run_manifest.py --manifest $manifest
        if ($LASTEXITCODE -ne 0) {
            throw "Manifest failed with exit code ${LASTEXITCODE}: $manifest"
        }
    }

    Write-Host ""
    Write-Host "[overnight-round2] complete"
}
finally {
    Stop-Transcript | Out-Null
}
