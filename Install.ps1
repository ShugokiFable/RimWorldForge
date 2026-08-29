[CmdletBinding()]
param(
  [switch]$SkipTests
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { throw 'Python 3.10+ was not found on PATH.' }
Write-Host '== RimWorldForge foundation install =='
Write-Host "root: $root"
& $py.Source --version
$venv = Join-Path $root '.venv'
if (-not (Test-Path (Join-Path $venv 'Scripts\python.exe'))) {
  & $py.Source -m venv $venv
  if ($LASTEXITCODE -ne 0) { throw "venv creation failed with exit code $LASTEXITCODE" }
}
$vpy = Join-Path $venv 'Scripts\python.exe'
& $vpy -m pip install --disable-pip-version-check -e $root
if ($LASTEXITCODE -ne 0) { throw "pip install failed with exit code $LASTEXITCODE" }
if (-not $SkipTests) {
  & $vpy (Join-Path $root 'tests\run_tests.py')
  if ($LASTEXITCODE -ne 0) { throw "tests failed with exit code $LASTEXITCODE" }
}
Write-Host ''
Write-Host 'Installed. Useful commands:'
Write-Host "  $vpy -m rwforge.cli doctor"
Write-Host "  $vpy -m rwforge.cli index"
Write-Host "  $vpy -m rwforge.cli capabilities"
Write-Host ''
Write-Host 'MCP command (keep disabled outside RimWorld work):'
Write-Host "  $vpy $(Join-Path $root 'mcp_server\server.py')"
Write-Host ''
Write-Host 'Agent skill source:'
Write-Host "  $(Join-Path $root 'skills\rimworld-forge\SKILL.md')"
