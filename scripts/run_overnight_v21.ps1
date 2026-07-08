param(
    [switch]$IncludeNeural
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $Root

$LogDir = Join-Path $Root "outputs\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TranscriptPath = Join-Path $LogDir "overnight_v21_$Stamp.log"

Start-Transcript -Path $TranscriptPath | Out-Null

try {
    Write-Host "[overnight] root: $Root"
    Write-Host "[overnight] transcript: $TranscriptPath"

    $manifests = @(
        ".\configs\experiments.finqa_600.local_planner_table_ops_v21.json",
        ".\configs\experiments.finqa_300.local_planner_strong_retrieval_baselines_v21.json"
    )

    if ($IncludeNeural) {
        $manifests += ".\configs\experiments.finqa_300.neural_retrieval_baselines_v21.json"
    }

    foreach ($manifest in $manifests) {
        Write-Host ""
        Write-Host "[overnight] running $manifest"
        python .\scripts\run_manifest.py --manifest $manifest
        if ($LASTEXITCODE -ne 0) {
            throw "Manifest failed with exit code ${LASTEXITCODE}: $manifest"
        }
    }

    Write-Host ""
    Write-Host "[overnight] complete"
}
finally {
    Stop-Transcript | Out-Null
}
