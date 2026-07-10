param(
    [string]$LatexPluginRoot = "$env:USERPROFILE\.codex\plugins\cache\openai-bundled\latex\0.2.2",
    [string]$OutputRoot = "",
    [switch]$KeepSandbox
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$paperRoot = Join-Path $repoRoot "paper"
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $repoRoot "outputs\latex_sandbox"
}

$sandboxPaper = Join-Path $OutputRoot "paper"
$buildDir = Join-Path $OutputRoot "build"
$compileScript = Join-Path $LatexPluginRoot "scripts\compile_latex.py"
$tectonicExe = Join-Path $LatexPluginRoot "bin\tectonic.exe"

if (-not (Test-Path -LiteralPath $compileScript)) {
    throw "Codex LaTeX compile helper not found: $compileScript"
}
if (-not (Test-Path -LiteralPath $tectonicExe)) {
    throw "Bundled Tectonic not found: $tectonicExe"
}

if ((Test-Path -LiteralPath $sandboxPaper) -and -not $KeepSandbox) {
    Remove-Item -LiteralPath $sandboxPaper -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $sandboxPaper | Out-Null
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

Copy-Item -LiteralPath (Join-Path $paperRoot "main.tex") -Destination $sandboxPaper -Force
Copy-Item -LiteralPath (Join-Path $paperRoot "appendix.tex") -Destination $sandboxPaper -Force
Copy-Item -LiteralPath (Join-Path $paperRoot "references.bib") -Destination $sandboxPaper -Force
Copy-Item -LiteralPath (Join-Path $paperRoot "generated") -Destination $sandboxPaper -Recurse -Force
Copy-Item -LiteralPath (Join-Path $paperRoot "figures") -Destination $sandboxPaper -Recurse -Force

$officialStyle = Join-Path $paperRoot "aaai27.sty"
if (Test-Path -LiteralPath $officialStyle) {
    Copy-Item -LiteralPath $officialStyle -Destination $sandboxPaper -Force
} else {
    @'
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{aaai27}[2026/07/10 compile-only stub]
\RequirePackage[margin=0.75in]{geometry}
\RequirePackage{caption}
\RequirePackage{booktabs}
\RequirePackage{graphicx}
\RequirePackage{times}
\RequirePackage{helvet}
\RequirePackage{courier}
'@ | Set-Content -LiteralPath (Join-Path $sandboxPaper "aaai27.sty") -Encoding ascii
    Write-Host "Official aaai27.sty was not found; using sandbox-only compile stub."
}

python $compileScript (Join-Path $sandboxPaper "main.tex") --compiler tectonic --output-directory $buildDir --json
