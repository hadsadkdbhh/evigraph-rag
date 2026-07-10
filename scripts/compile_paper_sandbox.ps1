param(
    [string]$LatexPluginRoot = "$env:USERPROFILE\.codex\plugins\cache\openai-bundled\latex\0.2.2",
    [string]$OutputRoot = "",
    [ValidateSet("main", "supplement")]
    [string]$Target = "main",
    [ValidateSet("auto", "tectonic", "texlive")]
    [string]$Compiler = "texlive",
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

if (-not (Test-Path -LiteralPath $compileScript)) {
    throw "Codex LaTeX compile helper not found: $compileScript"
}
if ($Compiler -in @("auto", "tectonic")) {
    $tectonicExe = Join-Path $LatexPluginRoot "bin\tectonic.exe"
    if (-not (Test-Path -LiteralPath $tectonicExe)) {
        throw "Bundled Tectonic not found: $tectonicExe"
    }
}

if ((Test-Path -LiteralPath $sandboxPaper) -and -not $KeepSandbox) {
    Remove-Item -LiteralPath $sandboxPaper -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $sandboxPaper | Out-Null
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

Copy-Item -LiteralPath (Join-Path $paperRoot "main.tex") -Destination $sandboxPaper -Force
Copy-Item -LiteralPath (Join-Path $paperRoot "supplement.tex") -Destination $sandboxPaper -Force
Copy-Item -LiteralPath (Join-Path $paperRoot "appendix.tex") -Destination $sandboxPaper -Force
Copy-Item -LiteralPath (Join-Path $paperRoot "references.bib") -Destination $sandboxPaper -Force
Copy-Item -LiteralPath (Join-Path $paperRoot "generated") -Destination $sandboxPaper -Recurse -Force
Copy-Item -LiteralPath (Join-Path $paperRoot "figures") -Destination $sandboxPaper -Recurse -Force

$officialStyle = Join-Path $paperRoot "aaai2027.sty"
$officialBibStyle = Join-Path $paperRoot "aaai2027.bst"
if (Test-Path -LiteralPath $officialStyle) {
    Copy-Item -LiteralPath $officialStyle -Destination $sandboxPaper -Force
    if (Test-Path -LiteralPath $officialBibStyle) {
        Copy-Item -LiteralPath $officialBibStyle -Destination $sandboxPaper -Force
    }
} else {
    @'
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{aaai2027}[2026/07/10 compile-only stub]
\DeclareOption{submission}{}
\ProcessOptions\relax
\RequirePackage[margin=0.75in]{geometry}
\RequirePackage{caption}
\RequirePackage{booktabs}
\RequirePackage{graphicx}
'@ | Set-Content -LiteralPath (Join-Path $sandboxPaper "aaai2027.sty") -Encoding ascii
    Write-Host "Official aaai2027.sty was not found; using sandbox-only compile stub."
    if (-not (Test-Path -LiteralPath $officialBibStyle)) {
        Write-Host "Official aaai2027.bst was not found; bibliography compile may fail until the official kit is added."
    }
}

$rootFile = Join-Path $sandboxPaper "$Target.tex"
if ($Compiler -eq "texlive") {
    python $compileScript $rootFile --compiler texlive --engine pdflatex --output-directory $buildDir --json
} elseif ($Compiler -eq "tectonic") {
    python $compileScript $rootFile --compiler tectonic --output-directory $buildDir --json
} else {
    python $compileScript $rootFile --output-directory $buildDir --json
}
