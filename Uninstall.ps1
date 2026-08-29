[CmdletBinding(SupportsShouldProcess=$true)]
param(
  # Installer may have registered the MCP in Claude Code's USER config (machine-wide).
  # Remove it by default; keep with -KeepMcp.
  [switch]$KeepMcp
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

if (-not $KeepMcp) {
  $claude = Get-Command claude -ErrorAction SilentlyContinue
  if ($claude) {
    $claudeErrorPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & claude mcp remove --scope user rimworldforge 2>$null | Out-Null
    $ErrorActionPreference = $claudeErrorPreference
    Write-Host 'removed rimworldforge MCP from Claude Code user config (if present)'
  }
}

foreach ($skill in @(
  (Join-Path $env:USERPROFILE '.claude\skills\rimworld-forge'),
  (Join-Path $env:USERPROFILE '.codex\skills\rimworld-forge'),
  (Join-Path $env:LOCALAPPDATA 'hermes\profiles\rimworld\skills\rimworld-forge')
)) {
  if (Test-Path $skill) { Remove-Item -LiteralPath $skill -Recurse -Force; Write-Host "removed $skill" }
}

$venv = Join-Path $root '.venv'
if (Test-Path $venv) {
  if ($PSCmdlet.ShouldProcess($venv, 'Remove RimWorldForge local virtual environment')) {
    Remove-Item -LiteralPath $venv -Recurse -Force
  }
}
Write-Host 'RimWorldForge stores generated workspaces only where you chose to create them.'
Write-Host 'No RimWorld files, saves, or active mod configuration are removed by this uninstaller.'
