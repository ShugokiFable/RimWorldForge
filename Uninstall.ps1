[CmdletBinding(SupportsShouldProcess=$true)]
param()
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }
$venv = Join-Path $root '.venv'
if (Test-Path $venv) {
  if ($PSCmdlet.ShouldProcess($venv, 'Remove RimWorldForge local virtual environment')) {
    Remove-Item -LiteralPath $venv -Recurse -Force
  }
}
Write-Host 'RimWorldForge stores generated workspaces only where you chose to create them.'
Write-Host 'No RimWorld files, saves, or active mod configuration are removed by this uninstaller.'
