#requires -Version 7.0
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$Destination
)

$ErrorActionPreference = 'Stop'
$sourceRoot = Join-Path $PSScriptRoot 'skill'
$targetRoot = [IO.Path]::GetFullPath($Destination).TrimEnd([char[]]'\/')
if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot 'SKILL.md'))) {
    throw 'Missing skill/SKILL.md.'
}
if ((Split-Path $targetRoot -Leaf) -ne 'scansci-svg' -or
    $targetRoot.StartsWith($sourceRoot, [StringComparison]::OrdinalIgnoreCase) -or
    $sourceRoot.StartsWith($targetRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Destination must be a separate directory named scansci-svg, outside the source tree.'
}
# Avoid silently following a link into unrelated storage during backup/copy.
foreach ($root in @($sourceRoot, $targetRoot)) {
    if (Test-Path -LiteralPath $root) {
        $entries = @((Get-Item -LiteralPath $root -Force)) + @(Get-ChildItem -LiteralPath $root -Recurse -Force)
        if ($entries | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) {
            throw "Linked files/directories require manual handling: $root"
        }
    }
}
if (-not $PSCmdlet.ShouldProcess($targetRoot, 'Back up existing installation and copy skill files without deletion')) { return }
if (Test-Path -LiteralPath $targetRoot) {
    $backupRoot = Join-Path $PSScriptRoot ('.local/install-backups/' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
    New-Item -ItemType Directory -Path $backupRoot | Out-Null
    Get-ChildItem -LiteralPath $targetRoot -Force | Copy-Item -Destination $backupRoot -Recurse -Force
    Write-Output "Previous installation saved: $backupRoot"
}
New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
foreach ($file in (Get-ChildItem -LiteralPath $sourceRoot -Recurse -File -Force | Where-Object { $_.FullName -notmatch '[\\/]__pycache__[\\/]' })) {
    $relative = [IO.Path]::GetRelativePath($sourceRoot, $file.FullName)
    $target = Join-Path $targetRoot $relative
    New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
    Copy-Item -LiteralPath $file.FullName -Destination $target -Force
}
Write-Output "Installed from $sourceRoot to $targetRoot. Destination-only files were retained."
