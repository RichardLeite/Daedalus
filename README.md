# Daedalus

> A personal, portable development configuration for OpenCode.

Daedalus provides a curated set of agents, skills, commands, rules, and templates
for software engineering. It is designed to be installed globally and extended
per project, without vendor-specific processes or credentials.

The name comes from Daedalus, the Greek inventor, architect, and craftsman.

## Status

`v0.1.0` is under active development. The initial release targets OpenCode only.
Claude Code and Codex adapters, long-term memory, and cross-repository workspaces
are planned for later releases.

## Requirements

- Python 3.11 or newer
- Git
- OpenCode
- GitHub CLI (`gh`), optional but recommended

## Quick install

Linux, macOS, and WSL2:

```bash
curl -fsSL https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.sh | bash
```

Windows (native PowerShell):

```powershell
iex (irm https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.ps1)
```

The installer is user-local and does not require admin rights. It:

1. Installs OpenCode when missing. On Windows it uses `winget` package
   `Anomaly.OpenCode` first. On Linux, macOS, and WSL2 it uses the official
   `https://opencode.ai/v2/install` script.
2. Downloads Daedalus to `~/.local/share/daedalus` or `%LOCALAPPDATA%\Daedalus`.
3. Bootstraps `uv` and Python 3.11 when needed.
4. Installs the `daedalus` CLI.
5. Runs `daedalus install --global --merge-config`.

> The installer installs the OpenCode **CLI**. The desktop app is separate:
> `winget install --id Anomaly.OpenCode.Desktop` or
> [opencode.ai/download](https://opencode.ai/download).
>
> Windows fallback order if `winget` is unavailable or fails: Git Bash with the
> official installer, `npm install -g @opencode/cli@latest`, then
> `mise use -g opencode`.

### Installer options

Linux, macOS, WSL2:

```bash
# Show the plan without changing files
curl -fsSL https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.sh | bash -s -- --dry-run

# Pin a tag
curl -fsSL https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.sh | bash -s -- --ref v0.1.0

# Install the CLI but skip the global config
curl -fsSL https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.sh | bash -s -- --no-global

# Do not install OpenCode
curl -fsSL https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.sh | bash -s -- --skip-opencode

# Remove the CLI and global config, keeping the data directory
curl -fsSL https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.sh | bash -s -- --uninstall
```

Windows:

```powershell
# Show the plan without changing files
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.ps1))) -DryRun

# Pin a tag
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.ps1))) -Ref v0.1.0

# Install the CLI but skip the global config
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.ps1))) -NoGlobal

# Do not install OpenCode
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.ps1))) -SkipOpencode
```

Read `install.sh` or `install.ps1` before piping it to a shell. Both are plain
scripts in this repository and support `--dry-run` / `-DryRun`.

## Install from source

Daedalus is currently installed from a source checkout:

```bash
git clone https://github.com/RichardLeite/Daedalus.git
cd Daedalus
uv tool install -e .
# or: pipx install -e .
```

Then install the global OpenCode configuration:

```bash
daedalus install --global --dry-run
daedalus install --global
```

The installer copies the core into `$XDG_CONFIG_HOME/opencode` or
`~/.config/opencode`, records a manifest, and backs up existing files before
changing anything.

Set `DAEDALUS_CONFIG_DIR` to use a different global configuration directory.
This is useful for tests and non-standard setups.

## Use

```bash
daedalus doctor                 # check the environment
daedalus validate               # validate agents, skills, commands, and config
daedalus validate --global      # validate the installed global config
daedalus context --json         # project context for the orchestrator
```

Inside a project:

```bash
daedalus init --plan            # show what would change
daedalus init                   # create the project layer
```

Or use the OpenCode command:

```text
/daedalus-init
```

## Commands

| Command | Purpose |
|---|---|
| `daedalus install --global` | Install the core into the global OpenCode config |
| `daedalus update --global` | Update managed files |
| `daedalus uninstall --global` | Remove managed files and restore backups |
| `daedalus init` | Create or update the project layer |
| `daedalus context` | Read project context |
| `daedalus doctor` | Diagnose the environment |
| `daedalus validate` | Validate the configuration |

## Layout

```text
Daedalus/
├── AGENTS.md                 # global instructions
├── CONVENTIONS.md            # engineering conventions
├── opencode.jsonc            # OpenCode V2 configuration
├── .opencode/
│   ├── agents/
│   ├── commands/
│   ├── skills/
│   ├── rules/
│   ├── templates/
│   └── profiles/
└── daedalus/                 # Python CLI
```

## Releases

Push a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The release workflow:

1. Verifies lint, tests, and configuration.
2. Checks that the tag matches the version in `pyproject.toml`.
3. Builds the wheel, the sdist, and a full source tarball.
4. Generates `SHA256SUMS`.
5. Creates or updates the GitHub Release with all artifacts.

Artifacts:

- `daedalus_opencode-<version>-py3-none-any.whl`
- `daedalus_opencode-<version>.tar.gz`
- `daedalus-<version>-source.tar.gz`
- `SHA256SUMS`

## Development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
pytest
python -m daedalus validate --root .
```

## License

MIT. See [LICENSE](LICENSE).
