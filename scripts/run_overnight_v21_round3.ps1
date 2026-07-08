param()

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $Root

$LogDir = Join-Path $Root "outputs\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TranscriptPath = Join-Path $LogDir "overnight_v21_round3_$Stamp.log"

Start-Transcript -Path $TranscriptPath | Out-Null

try {
    Write-Host "[overnight-round3] root: $Root"
    Write-Host "[overnight-round3] transcript: $TranscriptPath"
    Write-Host "[overnight-round3] running FinQA-600 v21 component ablation"

    python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_600.local_planner_ablation_v21.json
    if ($LASTEXITCODE -ne 0) {
        throw "Manifest failed with exit code ${LASTEXITCODE}: FinQA-600 v21 component ablation"
    }

    Write-Host ""
    Write-Host "[overnight-round3] complete"
}
finally {
    Stop-Transcript | Out-Null
}
