[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Yes,
    [switch]$NoGlobal,
    [switch]$NoMergeConfig,
    [switch]$SkipOpencode,
    [switch]$NoShell,
    [switch]$Uninstall,
    [string]$Ref = "main",
    [string]$Dir = "",
    [string]$Source = "",
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$Owner = "RichardLeite"
$Repo = "Daedalus"

if (-not [string]::IsNullOrWhiteSpace($Source)) {
    if (-not (Test-Path $Source)) { Fail "source directory not found: $Source" }
    $Dir = (Resolve-Path $Source).Path
} elseif ([string]::IsNullOrWhiteSpace($Dir)) {
    $Dir = Join-Path $env:LOCALAPPDATA "Daedalus"
}
$Dir = [Environment]::ExpandEnvironmentVariables($Dir)
if ($Dir.StartsWith("~")) {
    $Dir = Join-Path $HOME $Dir.Substring(2)
}

function Say([string]$Message) { Write-Host $Message }
function Warn([string]$Message) { Write-Warning $Message }
function Fail([string]$Message) { Write-Host "error: $Message" -ForegroundColor Red; exit 1 }

function Show-Usage {
    @"
Daedalus installer for native Windows.

Usage:
  iex (irm https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.ps1)

With options:
  & ([scriptblock]::Create((irm https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.ps1))) -DryRun

Options:
  -DryRun           Show what would happen and exit
  -Yes              Do not prompt
  -NoGlobal         Install the CLI but skip the global OpenCode config
  -NoMergeConfig    Do not merge an existing opencode.jsonc
  -SkipOpencode     Do not install OpenCode
  -NoShell          Do not modify the shell PATH configuration
  -Source <path>    Use a local Daedalus checkout instead of cloning
  -Uninstall        Remove the CLI and the global config
  -Ref <ref>        Branch or tag to install (default: main)
  -Dir <path>       Data directory (default: %LOCALAPPDATA%\Daedalus)
  -Help             Show this help
"@
}

function Add-UserPath([string]$PathToAdd) {
    if ([string]::IsNullOrWhiteSpace($PathToAdd)) { return }
    if (-not (Test-Path $PathToAdd)) { return }
    $current = [Environment]::GetEnvironmentVariable("Path", "User")
    if ([string]::IsNullOrWhiteSpace($current)) { $current = "" }
    $parts = $current -split ';' | Where-Object { $_ }
    if ($parts -notcontains $PathToAdd) {
        $newPath = (($parts + $PathToAdd) -join ';')
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    }
    if ($env:Path -notlike "*$PathToAdd*") {
        $env:Path = "$PathToAdd;$env:Path"
    }
}

function Add-OpenCodePaths {
    Add-UserPath (Join-Path $HOME ".opencode\bin")
    Add-UserPath (Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Links")
    Add-UserPath (Join-Path $env:APPDATA "npm")

    $packageRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
    if (Test-Path $packageRoot) {
        Get-ChildItem -Path $packageRoot -Directory -Filter "Anomaly.OpenCode_*" -ErrorAction SilentlyContinue |
            ForEach-Object { Add-UserPath $_.FullName }
    }
}

function Find-OpenCode {
    $command = Get-Command opencode -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }

    $candidates = @(
        (Join-Path $HOME ".opencode\bin\opencode.exe"),
        (Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Links\opencode.exe")
    )
    $packageRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
    if (Test-Path $packageRoot) {
        $candidates += Get-ChildItem -Path $packageRoot -Directory -Filter "Anomaly.OpenCode_*" -ErrorAction SilentlyContinue |
            ForEach-Object { Join-Path $_.FullName "opencode.exe" }
    }
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

if ($Help) {
    Show-Usage
    exit 0
}

Say "Daedalus installer"
Say "  os:       Windows ($env:PROCESSOR_ARCHITECTURE)"
Say "  ref:      $Ref"
if (-not [string]::IsNullOrWhiteSpace($Source)) {
    Say "  source:   $Dir"
}
Say "  data dir: $Dir"

if ($DryRun) {
    Say ""
    Say "Detected:"
    if (Get-Command git -ErrorAction SilentlyContinue) { Say "  git: yes" } else { Say "  git: no (will use archive)" }
    if (Get-Command uv -ErrorAction SilentlyContinue) { Say "  uv: yes" } else { Say "  uv: no (will bootstrap)" }
    if ($SkipOpencode) {
        Say "  opencode: skipped"
    } elseif (Find-OpenCode) {
        Say "  opencode: yes"
    } elseif (Get-Command winget -ErrorAction SilentlyContinue) {
        Say "  opencode: no (will install via winget: Anomaly.OpenCode)"
    } else {
        Say "  opencode: no (will use fallback installer)"
    }
    Say ""
    Say "Dry run: no files were changed."
    $dryArgs = "install --global"
    if (-not $NoMergeConfig) { $dryArgs += " --merge-config" }
    Say "Would install the CLI and run: daedalus $dryArgs"
    exit 0
}

if ($Uninstall) {
    $uninstallExe = $null
    $existing = Get-Command daedalus -ErrorAction SilentlyContinue
    if ($existing) {
        $uninstallExe = $existing.Source
    } elseif (Get-Command uv -ErrorAction SilentlyContinue) {
        $bin = (& uv tool dir --bin | Select-Object -First 1).Trim()
        $candidate = Join-Path $bin "daedalus.exe"
        if (Test-Path $candidate) { $uninstallExe = $candidate }
    }
    if ($uninstallExe) {
        & $uninstallExe uninstall --global
    } else {
        Warn "daedalus CLI not found"
    }
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        & uv tool uninstall daedalus-opencode 2>$null | Out-Null
    }
    Say "Daedalus CLI removed. Data kept at $Dir"
    Say "OpenCode was not removed."
    exit 0
}

$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("daedalus-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

try {
    function Ensure-OpenCode {
        if ($SkipOpencode) {
            Say "Skipping OpenCode installation (-SkipOpencode)."
            return
        }

        $existing = Find-OpenCode
        if ($existing) {
            $version = (& $existing --version 2>$null | Select-Object -First 1)
            $label = ""
            if (-not [string]::IsNullOrWhiteSpace($version)) { $label = ": $version" }
            Say "OpenCode already installed$label"
            Add-OpenCodePaths
            return
        }

        $installed = $false

        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Say "Installing OpenCode via winget (Anomaly.OpenCode)..."
            & winget install --id Anomaly.OpenCode --exact --accept-package-agreements --accept-source-agreements
            if ($LASTEXITCODE -eq 0) {
                $installed = $true
            } else {
                Warn "winget install failed; trying fallback methods."
            }
        }

        if (-not $installed) {
            $gitBash = $null
            if ($env:ProgramFiles) {
                $candidate = Join-Path $env:ProgramFiles "Git\bin\bash.exe"
                if (Test-Path $candidate) { $gitBash = $candidate }
            }
            if (-not $gitBash -and ${env:ProgramFiles(x86)}) {
                $candidate = Join-Path ${env:ProgramFiles(x86)} "Git\bin\bash.exe"
                if (Test-Path $candidate) { $gitBash = $candidate }
            }
            if ($gitBash) {
                Say "Installing OpenCode via the official installer (Git Bash)..."
                & $gitBash -lc "curl -fsSL https://opencode.ai/v2/install | bash"
                if ($LASTEXITCODE -eq 0) {
                    $installed = $true
                } else {
                    Warn "official installer failed; trying fallback methods."
                }
            }
        }

        if (-not $installed -and (Get-Command npm -ErrorAction SilentlyContinue)) {
            Say "Installing OpenCode via npm (@opencode/cli)..."
            & npm install -g "@opencode/cli@latest"
            if ($LASTEXITCODE -eq 0) {
                $installed = $true
            } else {
                Warn "npm install failed; trying fallback methods."
            }
        }

        if (-not $installed -and (Get-Command mise -ErrorAction SilentlyContinue)) {
            Say "Installing OpenCode via mise..."
            & mise use -g opencode
            if ($LASTEXITCODE -eq 0) {
                $installed = $true
            }
        }

        if (-not $installed) {
            Fail "Could not install OpenCode. Install winget (App Installer), Git for Windows, or Node/npm, then retry. See https://opencode.ai"
        }

        Add-OpenCodePaths

        $found = Find-OpenCode
        if ($found) {
            $version = (& $found --version 2>$null | Select-Object -First 1)
            $label = ""
            if (-not [string]::IsNullOrWhiteSpace($version)) { $label = ": $version" }
            Say "OpenCode installed$label"
        } else {
            Warn "OpenCode was installed but is not on PATH yet. Open a new terminal to use it."
        }
    }

    function Get-Source {
        if (-not [string]::IsNullOrWhiteSpace($Source)) {
            if (-not (Test-Path (Join-Path $Dir "pyproject.toml"))) {
                Fail "source is not a Daedalus checkout: $Dir"
            }
            Say "Using local source: $Dir"
            return
        }

        $gitDir = Join-Path $Dir ".git"
        if (Test-Path $gitDir) {
            if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
                Fail "git is required to update $Dir"
            }
            Say "Updating existing checkout..."
            & git -C $Dir fetch --depth 1 origin $Ref
            if ($LASTEXITCODE -ne 0) { Fail "git fetch failed" }
            & git -C $Dir checkout --detach FETCH_HEAD
            if ($LASTEXITCODE -ne 0) { Fail "git checkout failed" }
            return
        }

        if ((Test-Path (Join-Path $Dir "pyproject.toml")) -and (Test-Path (Join-Path $Dir ".opencode\agents"))) {
            Say "Using existing Daedalus directory: $Dir"
            return
        }

        if (Test-Path $Dir) {
            Fail "$Dir exists and is not a Daedalus checkout; choose another -Dir"
        }

        if (Get-Command git -ErrorAction SilentlyContinue) {
            Say "Cloning Daedalus into $Dir..."
            $parent = Split-Path -Parent $Dir
            if ($parent -and -not (Test-Path $parent)) {
                New-Item -ItemType Directory -Path $parent -Force | Out-Null
            }
            & git clone --depth 1 --branch $Ref "https://github.com/$Owner/$Repo.git" $Dir
            if ($LASTEXITCODE -ne 0) { Fail "git clone failed" }
            return
        }

        Say "git not found; downloading the source archive..."
        if ($Ref -like "v*") {
            $archive = "https://github.com/$Owner/$Repo/archive/refs/tags/$Ref.zip"
        } else {
            $archive = "https://github.com/$Owner/$Repo/archive/refs/heads/$Ref.zip"
        }
        $zip = Join-Path $TempDir "daedalus.zip"
        try {
            Invoke-WebRequest -Uri $archive -OutFile $zip -UseBasicParsing
        } catch {
            $archive = "https://github.com/$Owner/$Repo/archive/$Ref.zip"
            Invoke-WebRequest -Uri $archive -OutFile $zip -UseBasicParsing
        }
        Expand-Archive -Path $zip -DestinationPath $TempDir -Force
        $source = Get-ChildItem -Path $TempDir -Directory | Where-Object { $_.Name -like "$Repo-*" } | Select-Object -First 1
        if (-not $source) { Fail "could not extract the source archive" }
        New-Item -ItemType Directory -Path $Dir -Force | Out-Null
        Copy-Item -Path (Join-Path $source.FullName "*") -Destination $Dir -Recurse -Force
    }

    function Ensure-Uv {
        if (Get-Command uv -ErrorAction SilentlyContinue) { return }

        Say "uv not found. Installing uv from https://astral.sh/uv ..."
        if (-not $Yes) {
            $answer = Read-Host "Continue? [y/N]"
            if ($answer -notin @("y", "Y", "yes", "YES")) {
                Fail "uv is required to install Daedalus"
            }
        }

        $installer = Invoke-RestMethod -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing
        if ($NoShell) {
            $env:UV_NO_MODIFY_PATH = "1"
        }
        Invoke-Expression $installer
        $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
            Fail "uv installation failed"
        }
    }

    Ensure-OpenCode
    Get-Source
    Ensure-Uv

    Say "Installing the Daedalus CLI..."
    & uv python install 3.11
    if ($LASTEXITCODE -ne 0) { Fail "uv python install failed" }

    & uv tool install --force --python 3.11 -e $Dir
    if ($LASTEXITCODE -ne 0) { Fail "uv tool install failed" }

    $binDirOutput = & uv tool dir --bin
    if ($LASTEXITCODE -ne 0) { Fail "could not resolve the uv tool bin directory" }
    $binDir = ($binDirOutput | Select-Object -First 1).Trim()
    $env:Path = "$binDir;$env:Path"

    if ($NoShell) {
        Warn "Skipping shell PATH update (-NoShell); add $binDir to PATH."
    } else {
        & uv tool update-shell 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Warn "add $binDir to your PATH in the user environment"
        }
    }

    $daedalus = Join-Path $binDir "daedalus.exe"
    if (-not (Test-Path $daedalus)) {
        $daedalus = Join-Path $binDir "daedalus"
    }
    if (-not (Test-Path $daedalus)) {
        Fail "daedalus executable not found in $binDir"
    }

    if ($NoGlobal) {
        Say "Skipping global OpenCode configuration (-NoGlobal)."
    } else {
        Say "Installing the global OpenCode configuration..."
        $installArgs = @("install", "--global")
        if (-not $NoMergeConfig) {
            $installArgs += "--merge-config"
        }
        & $daedalus @installArgs
        if ($LASTEXITCODE -eq 3) {
            Fail "global install found conflicts; resolve them or run: `"$daedalus`" install --global --force"
        }
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }

    Say ""
    Say "Daedalus installed."
    Say "  CLI:  $daedalus"
    Say "  data: $Dir"
    Say "  bin:  $binDir"
    Say ""
    Say "Restart OpenCode, then run: daedalus doctor"
    Say "If the command is not on PATH, open a new terminal or add $binDir to PATH."
}
finally {
    Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
}
