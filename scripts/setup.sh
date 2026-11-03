#!/bin/bash

# Ask for the project author, write that into pyproject.toml, and, when git
# remote origin is set, point Source and the existing-issues link at it.
# Then install the Pixi environment.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYPROJECT="${ROOT}/pyproject.toml"

die() {
    printf '%s\n' "$*" >&2
    exit 1
}

trim() {
    local value=$1
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    printf '%s' "$value"
}

prompt_required() {
    local label=$1
    local name=$2
    local value
    while true; do
        if ! read -r -p "${label}: " value; then
            printf '\n' >&2
            die "Cancelled."
        fi
        value="$(trim "$value")"
        if [[ -n "$value" ]]; then
            printf -v "$name" '%s' "$value"
            return
        fi
        printf '%s is required.\n' "$label" >&2
    done
}

[[ -f "$PYPROJECT" ]] || die "Cannot find ${PYPROJECT}"

first=""
second=""
prompt_required "First name" first
prompt_required "Second name" second
if ! read -r -p "Email (optional): " email; then
    printf '\n' >&2
    die "Cancelled."
fi
email="$(trim "$email")"

origin=""
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    && origin="$(git -C "$ROOT" remote get-url origin 2>/dev/null)"; then
    origin="$(trim "$origin")"
fi

issues_link="$(
    SETUP_ROOT="$ROOT" \
    SETUP_PYPROJECT="$PYPROJECT" \
    SETUP_FIRST="$first" \
    SETUP_SECOND="$second" \
    SETUP_EMAIL="$email" \
    SETUP_ORIGIN="$origin" \
    python3 - <<'PY'
import os
import re
from pathlib import Path

path = Path(os.environ["SETUP_PYPROJECT"])
text = path.read_text()


def toml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


author = f"{{ name = {toml_string(os.environ['SETUP_FIRST'] + ' ' + os.environ['SETUP_SECOND'])}"
email = os.environ["SETUP_EMAIL"]
if email:
    author += f", email = {toml_string(email)}"
author += " }"
block = f"authors = [\n    {author},\n]"
text, author_count = re.subn(r"^authors = \[.*?\]", block, text, count=1, flags=re.M | re.S)
if author_count != 1:
    raise SystemExit("Could not find authors in pyproject.toml")

def issues_url(remote: str) -> str | None:
    cleaned = remote.strip().removesuffix(".git").rstrip("/")
    patterns = (
        r"git@(?P<host>[^:]+):(?P<path>.+)",
        r"ssh://(?:[^@/]+@)?(?P<host>[^/]+)/(?P<path>.+)",
        r"https?://(?P<host>[^/]+)/(?P<path>.+)",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, cleaned)
        if match is not None:
            return f"https://{match.group('host')}/{match.group('path')}/issues"
    return None


origin = os.environ["SETUP_ORIGIN"]
issues = ""
if origin:
    text, source_count = re.subn(
        r"^Source = .*$",
        f"Source = {toml_string(origin)}",
        text,
        count=1,
        flags=re.M,
    )
    if source_count != 1:
        raise SystemExit("Could not find Source in pyproject.toml")
    issues = issues_url(origin) or ""

path.write_text(text)

if issues:
    contributing = Path(os.environ["SETUP_ROOT"]) / ".github" / "CONTRIBUTING.md"
    guide = contributing.read_text()
    guide, link_count = re.subn(
        r"(\[existing issues\]\()[^)]+(\))",
        rf"\1{issues}\2",
        guide,
        count=1,
    )
    if link_count != 1:
        raise SystemExit("Could not find the existing-issues link in .github/CONTRIBUTING.md")
    contributing.write_text(guide)
    print(issues)
PY
)"

if [[ -n "$origin" ]]; then
    printf 'Set Source to %s\n' "$origin"
fi
if [[ -n "$issues_link" ]]; then
    printf 'Set existing-issues link to %s\n' "$issues_link"
elif [[ -n "$origin" ]]; then
    printf 'Left the existing-issues link unchanged. Could not build it from %s.\n' "$origin" >&2
fi
printf 'Set author to %s %s\n' "$first" "$second"

cd "$ROOT" || exit 1
pixi install
