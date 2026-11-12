#!/usr/bin/env bash
# Daedalus installer for Linux, macOS, and WSL2.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.sh | bash
#   curl -fsSL .../install.sh | bash -s -- --dry-run
#
# Options:
#   --dry-run           Show what would happen and exit
#   --yes, -y           Do not prompt
#   --no-global         Install the CLI but skip the global OpenCode config
#   --no-merge-config   Do not merge an existing opencode.jsonc
#   --uninstall         Remove the CLI and the global config
#   --ref <ref>         Branch or tag to install (default: main)
#   --dir <path>        Data directory (default: ~/.local/share/daedalus)
#   -h, --help          Show this help

set -euo pipefail

OWNER="RichardLeite"
REPO="Daedalus"
REF="${DAEDALUS_REF:-main}"
DATA_DIR="${DAEDALUS_HOME:-$HOME/.local/share/daedalus}"
DRY_RUN=0
ASSUME_YES=0
NO_GLOBAL=0
NO_MERGE=0
UNINSTALL=0
SKIP_OPENCODE=0
NO_SHELL=0
SOURCE=""
TMP_DIR=""

say() { printf '%s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

cleanup() {
  if [ -n "$TMP_DIR" ] && [ -d "$TMP_DIR" ]; then
    rm -rf "$TMP_DIR"
  fi
}
trap cleanup EXIT

usage() {
  cat <<'EOF'
Daedalus installer for Linux, macOS, and WSL2.

Usage:
  curl -fsSL https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.sh | bash

Options:
  --dry-run           Show what would happen and exit
  --yes, -y           Do not prompt
  --no-global         Install the CLI but skip the global OpenCode config
  --no-merge-config   Do not merge an existing opencode.jsonc
  --skip-opencode     Do not install OpenCode
  --no-shell          Do not modify the shell PATH configuration
  --source <path>     Use a local Daedalus checkout instead of cloning
  --uninstall         Remove the CLI and the global config
  --ref <ref>         Branch or tag to install (default: main)
  --dir <path>        Data directory (default: ~/.local/share/daedalus)
  -h, --help          Show this help
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --yes|-y) ASSUME_YES=1 ;;
    --no-global) NO_GLOBAL=1 ;;
    --no-merge-config) NO_MERGE=1 ;;
    --skip-opencode) SKIP_OPENCODE=1 ;;
    --no-shell) NO_SHELL=1 ;;
    --source)
      [ "$#" -ge 2 ] || die "--source requires a value"
      SOURCE="$2"
      shift
      ;;
    --uninstall) UNINSTALL=1 ;;
    --ref)
      [ "$#" -ge 2 ] || die "--ref requires a value"
      REF="$2"
      shift
      ;;
    --dir)
      [ "$#" -ge 2 ] || die "--dir requires a value"
      DATA_DIR="$2"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
  shift
done

case "$DATA_DIR" in
  "~/"*) DATA_DIR="$HOME/${DATA_DIR#\~/}" ;;
esac

OS="$(uname -s 2>/dev/null || echo unknown)"
ARCH="$(uname -m 2>/dev/null || echo unknown)"

say "Daedalus installer"
say "  os:       $OS ($ARCH)"
say "  ref:      $REF"
if [ -n "$SOURCE" ]; then
  say "  source:   $SOURCE"
fi
say "  data dir: $DATA_DIR"

if [ "$DRY_RUN" -eq 1 ]; then
  say ""
  say "Detected:"
  if command -v git >/dev/null 2>&1; then say "  git: yes"; else say "  git: no (will use archive)"; fi
  if command -v uv >/dev/null 2>&1; then say "  uv: yes"; else say "  uv: no (will bootstrap)"; fi
  if command -v curl >/dev/null 2>&1; then say "  curl: yes"; elif command -v wget >/dev/null 2>&1; then say "  wget: yes"; else say "  downloader: missing"; fi
  if [ "$SKIP_OPENCODE" -eq 1 ]; then
    say "  opencode: skipped"
  elif command -v opencode >/dev/null 2>&1; then
    say "  opencode: yes"
  else
    say "  opencode: no (will install)"
  fi
  say ""
  say "Dry run: no files were changed."
  say "Would install the CLI and run: daedalus install --global $([ "$NO_MERGE" -eq 0 ] && echo '--merge-config')"
  exit 0
fi

if [ "$UNINSTALL" -eq 1 ]; then
  DAEDALUS_BIN=""
  if command -v daedalus >/dev/null 2>&1; then
    DAEDALUS_BIN="$(command -v daedalus)"
  elif command -v uv >/dev/null 2>&1; then
    BIN_DIR="$(uv tool dir --bin)"
    if [ -x "$BIN_DIR/daedalus" ]; then
      DAEDALUS_BIN="$BIN_DIR/daedalus"
    elif [ -x "$BIN_DIR/daedalus.exe" ]; then
      DAEDALUS_BIN="$BIN_DIR/daedalus.exe"
    fi
  fi

  if [ -n "$DAEDALUS_BIN" ]; then
    "$DAEDALUS_BIN" uninstall --global || warn "global uninstall reported an issue"
  else
    warn "daedalus CLI not found"
  fi
  if command -v uv >/dev/null 2>&1; then
    uv tool uninstall daedalus-opencode >/dev/null 2>&1 || true
  fi
  say "Daedalus CLI removed. Data kept at $DATA_DIR"
  say "OpenCode was not removed."
  exit 0
fi

download() {
  url="$1"
  output="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$output"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$output" "$url"
  else
    die "curl or wget is required"
  fi
}

ensure_opencode() {
  if [ "$SKIP_OPENCODE" -eq 1 ]; then
    say "Skipping OpenCode installation (--skip-opencode)."
    return
  fi

  if command -v opencode >/dev/null 2>&1; then
    version="$(opencode --version 2>/dev/null | head -n 1 || true)"
    say "OpenCode already installed${version:+: $version}"
    PATH="$HOME/.opencode/bin:$PATH"
    export PATH
    return
  fi

  if [ -x "$HOME/.opencode/bin/opencode" ]; then
    version="$("$HOME/.opencode/bin/opencode" --version 2>/dev/null | head -n 1 || true)"
    say "OpenCode already installed${version:+: $version}"
    PATH="$HOME/.opencode/bin:$PATH"
    export PATH
    return
  fi

  say "Installing OpenCode from https://opencode.ai ..."
  TMP_DIR="${TMP_DIR:-$(mktemp -d)}"
  download "https://opencode.ai/v2/install" "$TMP_DIR/opencode-install.sh"
  bash "$TMP_DIR/opencode-install.sh"
  PATH="$HOME/.opencode/bin:$PATH"
  export PATH
  if ! command -v opencode >/dev/null 2>&1; then
    die "OpenCode installation failed; see https://opencode.ai"
  fi
  say "OpenCode installed: $(opencode --version 2>/dev/null | head -n 1 || echo 'ok')"
}

fetch_source() {
  if [ -n "$SOURCE" ]; then
    [ -d "$SOURCE" ] || die "source directory not found: $SOURCE"
    [ -f "$SOURCE/pyproject.toml" ] || die "source is not a Daedalus checkout: $SOURCE"
    DATA_DIR="$(cd "$SOURCE" && pwd)"
    say "Using local source: $DATA_DIR"
    return
  fi

  if [ -d "$DATA_DIR/.git" ]; then
    command -v git >/dev/null 2>&1 || die "git is required to update $DATA_DIR"
    say "Updating existing checkout..."
    git -C "$DATA_DIR" fetch --depth 1 origin "$REF"
    git -C "$DATA_DIR" checkout --detach FETCH_HEAD
    return
  fi

  if [ -f "$DATA_DIR/pyproject.toml" ] && [ -d "$DATA_DIR/.opencode/agents" ]; then
    say "Using existing Daedalus directory: $DATA_DIR"
    return
  fi

  if [ -e "$DATA_DIR" ]; then
    die "$DATA_DIR exists and is not a Daedalus checkout; choose another --dir"
  fi

  mkdir -p "$(dirname "$DATA_DIR")"
  if command -v git >/dev/null 2>&1; then
    say "Cloning Daedalus into $DATA_DIR..."
    git clone --depth 1 --branch "$REF" "https://github.com/$OWNER/$REPO.git" "$DATA_DIR"
    return
  fi

  say "git not found; downloading the source archive..."
  TMP_DIR="$(mktemp -d)"
  case "$REF" in
    v*) archive="https://github.com/$OWNER/$REPO/archive/refs/tags/$REF.tar.gz" ;;
    *) archive="https://github.com/$OWNER/$REPO/archive/refs/heads/$REF.tar.gz" ;;
  esac
  if ! download "$archive" "$TMP_DIR/daedalus.tar.gz"; then
    archive="https://github.com/$OWNER/$REPO/archive/$REF.tar.gz"
    download "$archive" "$TMP_DIR/daedalus.tar.gz"
  fi
  tar -xzf "$TMP_DIR/daedalus.tar.gz" -C "$TMP_DIR"
  src=""
  for candidate in "$TMP_DIR"/*; do
    if [ -d "$candidate" ]; then
      src="$candidate"
      break
    fi
  done
  [ -n "$src" ] || die "could not extract the source archive"
  mkdir -p "$DATA_DIR"
  cp -R "$src"/. "$DATA_DIR"/
}

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    return
  fi

  say "uv not found. Installing uv from https://astral.sh/uv ..."
  if [ "$ASSUME_YES" -eq 0 ] && [ -t 0 ]; then
    printf "Continue? [y/N] "
    read -r answer
    case "$answer" in
      y|Y|yes|YES) ;;
      *) die "uv is required to install Daedalus" ;;
    esac
  fi

  TMP_DIR="${TMP_DIR:-$(mktemp -d)}"
  download "https://astral.sh/uv/install.sh" "$TMP_DIR/uv-install.sh"
  if [ "$NO_SHELL" -eq 1 ]; then
    UV_NO_MODIFY_PATH=1 sh "$TMP_DIR/uv-install.sh"
  else
    sh "$TMP_DIR/uv-install.sh"
  fi
  PATH="$HOME/.local/bin:$PATH"
  export PATH
  command -v uv >/dev/null 2>&1 || die "uv installation failed"
}

ensure_opencode
fetch_source
ensure_uv

say "Installing the Daedalus CLI..."
uv python install 3.11
uv tool install --force --python 3.11 -e "$DATA_DIR"

BIN_DIR="$(uv tool dir --bin)"
PATH="$BIN_DIR:$PATH"
export PATH
if [ "$NO_SHELL" -eq 1 ]; then
  warn "Skipping shell PATH update (--no-shell); add $BIN_DIR to PATH."
else
  uv tool update-shell >/dev/null 2>&1 || warn "add $BIN_DIR to PATH in your shell profile"
fi

DAEDALUS_BIN="$BIN_DIR/daedalus"
if [ ! -x "$DAEDALUS_BIN" ] && [ -x "$BIN_DIR/daedalus.exe" ]; then
  DAEDALUS_BIN="$BIN_DIR/daedalus.exe"
fi
[ -x "$DAEDALUS_BIN" ] || die "daedalus executable not found in $BIN_DIR"

if [ "$NO_GLOBAL" -eq 1 ]; then
  say "Skipping global OpenCode configuration (--no-global)."
else
  say "Installing the global OpenCode configuration..."
  if [ "$NO_MERGE" -eq 1 ]; then
    "$DAEDALUS_BIN" install --global || {
      status=$?
      if [ "$status" -eq 3 ]; then
        die "global install found conflicts; resolve them or run: $DAEDALUS_BIN install --global --force"
      fi
      exit "$status"
    }
  else
    "$DAEDALUS_BIN" install --global --merge-config || {
      status=$?
      if [ "$status" -eq 3 ]; then
        die "global install found conflicts; resolve them or run: $DAEDALUS_BIN install --global --force"
      fi
      exit "$status"
    }
  fi
fi

say ""
say "Daedalus installed."
say "  CLI:  $DAEDALUS_BIN"
say "  data: $DATA_DIR"
say "  bin:  $BIN_DIR"
say ""
say "Restart OpenCode, then run: daedalus doctor"
say "If the command is not on PATH, open a new terminal or add $BIN_DIR to PATH."
