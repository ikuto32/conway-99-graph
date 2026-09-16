param([string]$Architecture = "sm_89")
$ErrorActionPreference = "Stop"
$source = Join-Path $PSScriptRoot "overlap_gpu.cu"
$target = Join-Path $PSScriptRoot "overlap_gpu.exe"
$nvcc = (Get-Command nvcc -ErrorAction Stop).Source
$vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
$installation = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $installation) { throw "Visual Studio C++ tools not found" }
$developerCommand = Join-Path $installation "Common7\Tools\VsDevCmd.bat"
# Import the compiler's environment without opening a visible helper window.
$environmentLines = & $env:ComSpec /d /c "call `"$developerCommand`" -no_logo -arch=x64 -host_arch=x64 >nul && set"
if ($LASTEXITCODE -ne 0) { throw "Could not initialize Visual Studio compiler environment" }
foreach ($line in $environmentLines) {
    if ($line -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], "Process")
    }
}
& $nvcc -O3 -std=c++17 "-arch=$Architecture" -Xcompiler /O2 -Xcompiler /utf-8 $source -o $target
if ($LASTEXITCODE -ne 0) { throw "nvcc build failed ($LASTEXITCODE)" }
Write-Output $target
