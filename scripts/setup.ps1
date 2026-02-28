$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $RootDir

if (Get-Command py -ErrorAction SilentlyContinue) {
  py -3 scripts/bootstrap.py @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  python scripts/bootstrap.py @args
} else {
  Write-Error "Python not found. Install Python 3.9+ first."
}
