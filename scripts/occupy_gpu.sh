#!/usr/bin/bash

# Stop compute processes on one GPU, except the PIDs given on the command line.
# The kernel rejects signals for processes this user cannot signal.
#
# scripts/occupy_gpu.sh GPU_ID PID [PID...]

set -uo pipefail

die() {
    printf '%s\n' "$*" >&2
    exit 1
}

usage() {
    cat >&2 <<'EOF'
Usage: scripts/occupy_gpu.sh GPU_ID PID [PID...]

Terminate compute processes on GPU_ID except the listed PIDs.
A signal the kernel rejects is reported, and the script exits non-zero.

    scripts/occupy_gpu.sh 0 12345 12346
EOF
}

trim() {
    local value="$1"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    printf '%s' "$value"
}

require_pid() {
    [[ "$1" =~ ^[1-9][0-9]*$ ]] || die "PID must be a positive integer, got '$1'."
}

if [[ $# -lt 2 ]]; then
    usage
    exit 1
fi

gpu_id="$1"
shift
[[ "$gpu_id" =~ ^[0-9]+$ ]] || die "GPU_ID must be an integer, got '${gpu_id}'."

declare -A keep=()
for pid in "$@"; do
    require_pid "$pid"
    keep["$pid"]=1
done

gpu_table="$(nvidia-smi --query-gpu=index,uuid --format=csv,noheader,nounits)" \
    || die "nvidia-smi failed while listing GPUs."
apps_table="$(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader,nounits)" \
    || die "nvidia-smi failed while listing compute processes."

gpu_uuid=""
while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    index="$(trim "${line%%,*}")"
    uuid="$(trim "${line#*,}")"
    if [[ "$index" == "$gpu_id" ]]; then
        gpu_uuid="$uuid"
        break
    fi
done <<<"$gpu_table"
[[ -n "$gpu_uuid" ]] || die "No GPU with index ${gpu_id}."

declare -a targets=()
while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    uuid="$(trim "${line%%,*}")"
    holder="$(trim "${line#*,}")"
    [[ "$uuid" == "$gpu_uuid" ]] || continue
    [[ -n "$holder" && "$holder" != "[N/A]" ]] || continue
    [[ -n "${keep[$holder]:-}" ]] && continue
    targets+=("$holder")
done <<<"$apps_table"

if [[ ${#targets[@]} -eq 0 ]]; then
    printf 'GPU %s has no compute process outside the given PIDs.\n' "$gpu_id"
    exit 0
fi

failed=0
for pid in "${targets[@]}"; do
    if kill -TERM "$pid" 2>/dev/null; then
        printf 'Sent TERM to %s on GPU %s.\n' "$pid" "$gpu_id"
    else
        printf 'Could not signal %s on GPU %s.\n' "$pid" "$gpu_id" >&2
        failed=1
    fi
done

sleep 1

for pid in "${targets[@]}"; do
    [[ -d "/proc/${pid}" ]] || continue
    if kill -KILL "$pid" 2>/dev/null; then
        printf 'Sent KILL to %s on GPU %s.\n' "$pid" "$gpu_id"
    else
        printf 'Could not signal %s on GPU %s.\n' "$pid" "$gpu_id" >&2
        failed=1
    fi
done

exit "$failed"
