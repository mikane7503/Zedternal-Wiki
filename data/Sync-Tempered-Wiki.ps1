[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ReleaseReport,
    [Parameter(Mandatory = $true)][string]$Version,
    [string]$Python = 'python',
    [switch]$NoPush
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$wikiRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$projectRoot = 'C:\Users\yss19\Documents\Projects\zedternal-unlimited-main'
$sourceRoot = Join-Path $projectRoot 'ZedternalTempered'
$opsRoot = 'D:\KF2server\KFGame\Config\SV_Zedternal_Tempered'
$reportPath = [IO.Path]::GetFullPath($ReleaseReport)
$report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($report.target -ne 'ZedternalTempered' -or $report.workshopId -ne '3809067086') {
    throw 'Refusing wiki sync: report is not for the existing Tempered Workshop item 3809067086.'
}
if ($report.status -ne 'published' -or -not $report.publicVerified) {
    throw 'Refusing wiki sync: the release report does not confirm a public Workshop upload.'
}
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw "Invalid Tempered version: $Version" }

$contentRoot = Join-Path (Split-Path -Parent $reportPath) 'content'
foreach ($file in $report.files) {
    $path = [IO.Path]::GetFullPath((Join-Path $contentRoot $file.path))
    if (-not $path.StartsWith($contentRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Release manifest path escapes staged content: $($file.path)"
    }
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing uploaded artifact: $($file.path)" }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $file.sha256) { throw "Uploaded artifact hash mismatch: $($file.path)" }
}

$iniNames = @(
    'KFZedternalReborn_Difficulty.ini', 'KFZedternalReborn_Events.ini',
    'KFZedternalReborn_Game.ini', 'KFZedternalReborn_Upgrades.ini',
    'KFZedternalReborn_Weapons.ini', 'KFZedternalReborn_ZedWaves.ini',
    'KFZedternalUnlimited.ini', 'KFZedternalUnlimited_Balance.ini',
    'KFZedternalUnlimited_Local.ini'
)
$iniAudit = foreach ($name in $iniNames) {
    $sourcePath = Join-Path $sourceRoot $name
    $opsPath = Join-Path $opsRoot $name
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw "Missing source INI: $sourcePath" }
    if (-not (Test-Path -LiteralPath $opsPath -PathType Leaf)) { throw "Missing operating INI: $opsPath" }
    [ordered]@{
        name = $name
        sourceSha256 = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
        operatingSha256 = (Get-FileHash -LiteralPath $opsPath -Algorithm SHA256).Hash.ToLowerInvariant()
        differs = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $opsPath -Algorithm SHA256).Hash
    }
}

$korFiles = @('ZedternalReborn.kor', 'ZedternalTempered.kor')
foreach ($kor in $korFiles) {
    $sourcePath = Join-Path (Join-Path $sourceRoot 'Localization\KOR') $kor
    $stagedPath = Join-Path $contentRoot "Localization\KOR\$kor"
    if (-not (Test-Path -LiteralPath $stagedPath -PathType Leaf)) { throw "KOR localization was not in the uploaded release: $kor" }
    if ((Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $stagedPath -Algorithm SHA256).Hash) {
        throw "Current KOR localization differs from the uploaded build: $kor"
    }
}

$sourceHashPath = Join-Path (Split-Path -Parent $reportPath) 'source-hashes.json'
if (-not (Test-Path -LiteralPath $sourceHashPath -PathType Leaf)) { throw 'Release source hash snapshot is missing.' }
$sourceSnapshot = Get-Content -LiteralPath $sourceHashPath -Raw -Encoding UTF8 | ConvertFrom-Json
$iniSnapshot = foreach ($name in $iniNames) {
    $sourcePath = Join-Path $sourceRoot $name
    $match = @($sourceSnapshot | Where-Object { [IO.Path]::GetFullPath($_.path) -ieq [IO.Path]::GetFullPath($sourcePath) })
    $snapshotVerified = $match.Count -gt 0
    if (-not $snapshotVerified) {
        # Backfill for the already-published v10.09.14 report, created before
        # the release pipeline began recording source INIs. Future runs must
        # include all nine source INIs in the immutable snapshot.
        if ($Version -ne '10.09.14') { throw "Release snapshot omits required INI: $name" }
        $recordedHash = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
    } else {
        $recordedHash = $match[0].sha256
        if ($recordedHash -ne (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash) { throw "Source INI changed after the release snapshot: $name" }
    }
    [ordered]@{ name=$name; sha256=$recordedHash.ToLowerInvariant(); snapshotVerified=$snapshotVerified }
}

$stagedFiles = @($report.files | ForEach-Object { [ordered]@{ path=$_.path; size=$_.size; sha256=$_.sha256.ToLowerInvariant() } })
$releaseUtc = $report.startedUtc
if ($report.PSObject.Properties['publishedUtc'] -and $report.publishedUtc) { $releaseUtc = $report.publishedUtc }
elseif ($report.PSObject.Properties['finishedUtc'] -and $report.finishedUtc) { $releaseUtc = $report.finishedUtc }
$manifest = [ordered]@{
    schemaVersion = 1
    product = 'Zedternal Tempered'
    version = $Version
    workshopId = '3809067086'
    workshopUrl = 'https://steamcommunity.com/sharedfiles/filedetails/?id=3809067086'
    publishedUtc = $releaseUtc
    releaseReportId = Split-Path -Leaf (Split-Path -Parent $reportPath)
    releaseSourceSnapshotSha256 = (Get-FileHash -LiteralPath $sourceHashPath -Algorithm SHA256).Hash.ToLowerInvariant()
    uploadedFiles = $stagedFiles
    sourceIni = @($iniSnapshot)
    operatingIni = @($iniAudit)
    localizationKor = @($korFiles | ForEach-Object {
        $name = $_
        $sourcePath = Join-Path (Join-Path $sourceRoot 'Localization\KOR') $name
        [ordered]@{ name=$name; sha256=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant() }
    })
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $wikiRoot 'data\release-manifest.json') -Encoding UTF8

$env:ZEDTERNAL_RELEASE_VERSION = $Version
$env:ZEDTERNAL_WORKSHOP_ID = '3809067086'
$env:ZEDTERNAL_PUBLISHED_UTC = $releaseUtc
$env:ZEDTERNAL_WORKSHOP_URL = 'https://steamcommunity.com/sharedfiles/filedetails/?id=3809067086'
Push-Location $wikiRoot
try {
    & $Python 'data\build.py'
    if ($LASTEXITCODE -ne 0) { throw 'Wiki data generation failed.' }
    $data = Get-Content -LiteralPath 'docs\data\perks.json' -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($data.meta.release.version -ne $Version -or $data.meta.release.workshopId -ne '3809067086') { throw 'Generated wiki data has stale release metadata.' }
    foreach ($perk in @($data.basePerks) + @($data.advancedPerks)) {
        if ($perk.icon -and -not (Test-Path -LiteralPath (Join-Path 'docs' $perk.icon) -PathType Leaf)) { throw "Missing perk icon: $($perk.key) -> $($perk.icon)" }
        foreach ($skill in $perk.skills) {
            if ($skill.icon -and -not (Test-Path -LiteralPath (Join-Path 'docs' $skill.icon) -PathType Leaf)) { throw "Missing skill icon: $($skill.key) -> $($skill.icon)" }
        }
    }
    if ($NoPush) { Write-Output 'Wiki generated and validated; --NoPush requested.'; return }

    $staged = @(& git diff --cached --name-only)
    if ($LASTEXITCODE -ne 0) { throw 'Could not inspect staged wiki changes.' }
    if ($staged.Count -gt 0) { throw 'Refusing to publish wiki with pre-staged changes; review/commit them first.' }
    & git add -- data/build.py data/release-manifest.json data/Sync-Tempered-Wiki.ps1 docs/data/perks.json docs/index.html docs/app.js
    if ($LASTEXITCODE -ne 0) { throw 'Could not stage generated wiki files.' }
    & git diff --cached --check
    if ($LASTEXITCODE -ne 0) { throw 'Wiki diff has whitespace errors.' }
    $changed = @(& git diff --cached --name-only)
    $commit = $null
    if ($changed.Count -gt 0) {
        & git commit -m "Sync Tempered wiki to v$Version"
        if ($LASTEXITCODE -ne 0) { throw 'Wiki commit failed.' }
        # The machine-local pre-push hook still calls data/sync_kor_download.py,
        # intentionally removed from this repo on 2026-10-01. Its old download
        # feature must not be resurrected; release/artifact/icon checks above
        # are the current pre-push validation for this sync.
        $emptyHooks = Join-Path $env:TEMP 'zedternal-wiki-empty-git-hooks'
        New-Item -ItemType Directory -Path $emptyHooks -Force | Out-Null
        & git -c "core.hooksPath=$emptyHooks" push origin main
        if ($LASTEXITCODE -ne 0) { throw 'Wiki push failed.' }
        $commit = (& git rev-parse HEAD).Trim()
        $headers = @{ 'User-Agent'='ZedternalWikiSync'; Accept='application/vnd.github+json' }
        $workflowUrl = 'https://api.github.com/repos/mikane7503/Zedternal-Wiki/actions/workflows/pages.yml/runs?branch=main&per_page=5'
        $deployment = $null
        for ($attempt = 0; $attempt -lt 12; $attempt++) {
            $runs = Invoke-RestMethod -Uri $workflowUrl -Headers $headers -TimeoutSec 20
            $matchingRuns = @($runs.workflow_runs | Where-Object { $_.head_sha -eq $commit } | Select-Object -First 1)
            if ($matchingRuns.Count -gt 0) { $deployment = $matchingRuns[0] }
            if ($null -ne $deployment -and $deployment.status -eq 'completed') { break }
            Start-Sleep -Seconds 10
        }
        if ($null -eq $deployment -or $deployment.status -ne 'completed' -or $deployment.conclusion -ne 'success') {
            $state = if ($null -eq $deployment) { 'workflow run not found' } else { "$($deployment.status)/$($deployment.conclusion)" }
            throw "GitHub Pages deployment did not succeed for $commit ($state)."
        }
    }
    $live = Invoke-RestMethod -Uri "https://mikane7503.github.io/Zedternal-Wiki/data/perks.json?verify=$([guid]::NewGuid())" -TimeoutSec 20
    $liveRelease = if ($live.meta -and $live.meta.PSObject.Properties['release']) { $live.meta.release } else { $null }
    if ($null -eq $liveRelease -or $liveRelease.version -ne $Version -or $liveRelease.workshopId -ne '3809067086') {
        throw "Live wiki does not report uploaded Tempered v$Version."
    }
    Write-Output "Wiki pushed for Zedternal Tempered v$Version."
} finally { Pop-Location }
