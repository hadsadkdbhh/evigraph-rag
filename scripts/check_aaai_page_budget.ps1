param(
    [string]$OutputRoot = "",
    [switch]$AlsoCompileSupplement
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $repoRoot "outputs\latex_sandbox"
}

$compileScript = Join-Path $PSScriptRoot "compile_paper_sandbox.ps1"
$mainPdf = Join-Path $OutputRoot "build\main.pdf"
$suppPdf = Join-Path $OutputRoot "build\supplement.pdf"
$officialStyle = Join-Path $repoRoot "paper\aaai2027.sty"

function Add-ToolPathIfPresent {
    param([string]$Path)
    if ((Test-Path -LiteralPath $Path) -and (($env:PATH -split ';') -notcontains $Path)) {
        $env:PATH = "$Path;$env:PATH"
    }
}

Add-ToolPathIfPresent "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
Add-ToolPathIfPresent "C:\Program Files\MiKTeX\miktex\bin\x64"
Add-ToolPathIfPresent "C:\Strawberry\perl\bin"
Add-ToolPathIfPresent "C:\Strawberry\c\bin"

function Assert-CommandAvailable {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. Install TeX Live/MiKTeX plus Poppler tools before running the official AAAI page-budget check."
    }
}

function Get-PdfPageCount {
    param([string]$PdfPath)
    $info = & pdfinfo $PdfPath
    $line = $info | Where-Object { $_ -match '^Pages:\s+(\d+)' } | Select-Object -First 1
    if (-not $line) {
        throw "Could not read PDF page count from $PdfPath"
    }
    return [int]($Matches[1])
}

function Find-ReferencesPage {
    param(
        [string]$PdfPath,
        [int]$PageCount
    )
    for ($page = 1; $page -le $PageCount; $page++) {
        $text = & pdftotext -f $page -l $page $PdfPath -
        if (($text -join "`n") -match '(?m)^\s*References\s*$') {
            return $page
        }
    }
    return $null
}

Assert-CommandAvailable "pdflatex"
Assert-CommandAvailable "bibtex"
Assert-CommandAvailable "pdfinfo"
Assert-CommandAvailable "pdftotext"

Write-Host "Compiling main paper..."
if (Test-Path -LiteralPath $mainPdf) {
    Remove-Item -LiteralPath $mainPdf -Force
}
& powershell -ExecutionPolicy Bypass -File $compileScript -Target main -Compiler texlive -OutputRoot $OutputRoot | Out-Host

if (-not (Test-Path -LiteralPath $mainPdf)) {
    throw "Main PDF not found after compile: $mainPdf"
}

$mainPagesTotal = Get-PdfPageCount $mainPdf
$referencesPage = Find-ReferencesPage $mainPdf $mainPagesTotal
if ($referencesPage) {
    $mainContentPages = $referencesPage - 1
} else {
    $mainContentPages = $mainPagesTotal
}

$usesOfficialStyle = Test-Path -LiteralPath $officialStyle

Write-Host ""
Write-Host "AAAI page-budget check"
Write-Host "----------------------"
Write-Host "PDF: $mainPdf"
Write-Host "Official aaai2027.sty present: $usesOfficialStyle"
Write-Host "Total pages: $mainPagesTotal / 9"
if ($referencesPage) {
    Write-Host "References start page: $referencesPage"
} else {
    Write-Host "References start page: not detected"
}
Write-Host "Estimated main-content pages: $mainContentPages / 7"

$failed = $false
if ($mainPagesTotal -gt 9) {
    Write-Host "FAIL: total paper length exceeds 9 pages."
    $failed = $true
}
if ($mainContentPages -gt 7) {
    Write-Host "FAIL: estimated main content exceeds 7 pages before references."
    $failed = $true
}
if (-not $usesOfficialStyle) {
    Write-Host "WARN: official AAAI style file is missing; sandbox count is only a smoke test."
}

if ($AlsoCompileSupplement) {
    Write-Host ""
    Write-Host "Compiling supplement..."
    if (Test-Path -LiteralPath $suppPdf) {
        Remove-Item -LiteralPath $suppPdf -Force
    }
    & powershell -ExecutionPolicy Bypass -File $compileScript -Target supplement -Compiler texlive -OutputRoot $OutputRoot | Out-Host
    if (Test-Path -LiteralPath $suppPdf) {
        $suppPages = Get-PdfPageCount $suppPdf
        Write-Host "Supplement PDF: $suppPdf"
        Write-Host "Supplement pages: $suppPages"
    } else {
        Write-Host "WARN: supplement PDF not found after compile: $suppPdf"
    }
}

if ($failed) {
    exit 1
}
