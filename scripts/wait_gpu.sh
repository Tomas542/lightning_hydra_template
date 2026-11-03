#!/usr/bin/bash

# Wait for one process to exit, or for one GPU to have no compute process,
# then start an experiment with pixi on that GPU.
#
# Pass exactly one of --pid and --gpu. The command after -- is handed to
# `pixi run`. CUDA_VISIBLE_DEVICES is set only for that child.
#
# scripts/wait_launch.sh --pid 12345 -- python -m src.train --config-name ns_codec
# scripts/wait_launch.sh --gpu 0 -- python -m src.train --config-name suppress

set -uo pipefail

# Seconds between checks. A positive number, a sleep suffix such as 2m,
# or an integer expression such as 2*60. sleep itself does not evaluate 2*60.
POLL_SECONDS=60
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

die() {
    printf '%s\n' "$*" >&2
    exit 1
}

usage() {
    cat >&2 <<'EOF'
Usage: scripts/wait_launch.sh (--pid PID | --gpu INDEX) -- COMMAND...

Wait until PID exits, or until GPU INDEX has no compute process, then run
COMMAND through pixi on that GPU.

    scripts/wait_launch.sh --pid 12345 -- python -m src.train --config-name ns_codec
    scripts/wait_launch.sh --gpu 4 -- python -m src.train --config-name suppress
EOF
}

log() {
    printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

trim() {
    local value="$1"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    printf '%s' "$value"
}

pid_running() {
    local stat rest state
    [[ -r "/proc/$1/stat" ]] || return 1
    stat="$(<"/proc/$1/stat")" || return 1
    rest="${stat#*)}"
    rest="${rest#"${rest%%[![:space:]]*}"}"
    state="${rest%% *}"
    [[ -n "$state" && "$state" != "Z" ]]
}

refresh_gpu_state() {
    gpu_table="$(nvidia-smi --query-gpu=index,uuid --format=csv,noheader,nounits)" \
        || die "nvidia-smi failed while listing GPUs."
    if ! apps_table="$(nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader,nounits)"; then
        die "nvidia-smi failed while listing compute processes."
    fi
}

uuid_for_index() {
    local index="$1" line idx uuid
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        idx="$(trim "${line%%,*}")"
        uuid="$(trim "${line#*,}")"
        if [[ "$idx" == "$index" ]]; then
            printf '%s' "$uuid"
        return 0
        fi
    done <<<"$gpu_table"
    return 1
}

index_for_uuid() {
    local want="$1" line idx uuid
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        idx="$(trim "${line%%,*}")"
        uuid="$(trim "${line#*,}")"
        if [[ "$uuid" == "$want" ]]; then
            printf '%s' "$idx"
            return 0
        fi
    done <<<"$gpu_table"
    return 1
}

collect_pids_on_uuid() {
    local want="$1" line uuid holder
    holders=()
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        uuid="$(trim "${line%%,*}")"
        holder="$(trim "${line#*,}")"
        if [[ "$uuid" == "$want" && -n "$holder" && "$holder" != "[N/A]" ]]; then
            holders+=("$holder")
        fi
    done <<<"$apps_table"
}

collect_indexes_for_pid() {
    local target="$1" line uuid holder index
    local -A seen=()
    owned=()
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        uuid="$(trim "${line%%,*}")"
        holder="$(trim "${line#*,}")"
        [[ "$holder" == "$target" ]] || continue
        if ! index="$(index_for_uuid "$uuid")"; then
            die "PID ${target} is on ${uuid}, which is not in the GPU list."
        fi
        if [[ -z "${seen[$index]:-}" ]]; then
            seen["$index"]=1
            owned+=("$index")
        fi
    done <<<"$apps_table"
}

quoted_command() {
    local part
    for part in "$@"; do
        printf '%q ' "$part"
    done
}

require_number() {
    [[ "$2" =~ ^[0-9]+$ ]] || die "$1 must be an integer, got '$2'."
}

require_poll_seconds() {
    local raw="$POLL_SECONDS" number resolved
    if [[ "$raw" =~ ^([0-9]+([.][0-9]+)?)([smhd])?$ ]]; then
        number="${BASH_REMATCH[1]}"
        if [[ "$number" =~ ^0+([.]0+)?$ ]]; then
            die "POLL_SECONDS must be a positive time, got '${raw}'."
        fi
        return 0
    fi
    if [[ "$raw" =~ ^[0-9[:space:]+*/().-]+$ ]]; then
        if ! resolved="$((raw))"; then
            die "POLL_SECONDS must be a positive time, got '${raw}'."
        fi
        if [[ ! "$resolved" =~ ^[1-9][0-9]*$ ]]; then
            die "POLL_SECONDS must be a positive number of seconds, got '${raw}'."
        fi
        POLL_SECONDS="$resolved"
        return 0
    fi
    die "POLL_SECONDS must be a positive time sleep accepts, or an integer expression such as 2*60. Got '${raw}'."
}

read_option_value() {
    [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || die "Missing value for $1."
    option_value="$2"
}

require_poll_seconds

pid=""
gpu=""
saw_pid=0
saw_gpu=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --pid)
            read_option_value "$1" "${2:-}"
            shift 2
            saw_pid=$((saw_pid + 1))
            pid="$option_value"
            ;;
        --pid=*)
            option_value="${1#--pid=}"
            [[ -n "$option_value" ]] || die "Missing value for --pid."
            shift
            saw_pid=$((saw_pid + 1))
            pid="$option_value"
        ;;
        --gpu)
            read_option_value "$1" "${2:-}"
            shift 2
            saw_gpu=$((saw_gpu + 1))
            gpu="$option_value"
        ;;
        --gpu=*)
            option_value="${1#--gpu=}"
            [[ -n "$option_value" ]] || die "Missing value for --gpu."
            shift
            saw_gpu=$((saw_gpu + 1))
            gpu="$option_value"
        ;;
        --)
            shift
            break
        ;;
        -h | --help)
            usage
            exit 0
        ;;
        -*)
            usage
            die "Unknown option: $1"
        ;;
        *)
            break
        ;;
    esac
done

if [[ "$saw_pid" -gt 1 || "$saw_gpu" -gt 1 ]]; then
    die "Pass --pid or --gpu once."
fi
if [[ -n "$pid" && -n "$gpu" ]]; then
    usage
    die "Pass either --pid or --gpu, not both."
fi
if [[ -z "$pid" && -z "$gpu" ]]; then
    usage
    die "Pass either --pid or --gpu."
fi
if [[ $# -eq 0 ]]; then
    usage
    die "Pass the experiment command after the wait option."
fi

if [[ -n "$pid" ]]; then
    require_number "PID" "$pid"
    if ! pid_running "$pid"; then
        die "PID ${pid} is not running."
    fi
    refresh_gpu_state
    collect_indexes_for_pid "$pid"
    if [[ "${#owned[@]}" -eq 0 ]]; then
        die "PID ${pid} is running but not using a GPU."
    fi
    if [[ "${#owned[@]}" -gt 1 ]]; then
        die "PID ${pid} uses more than one GPU: ${owned[*]}."
    fi
    gpu="${owned[0]}"
    if ! uuid="$(uuid_for_index "$gpu")"; then
        die "GPU ${gpu} disappeared from nvidia-smi."
    fi
    collect_pids_on_uuid "$uuid"
    others=()
    if [[ "${#holders[@]}" -gt 0 ]]; then
        for holder in "${holders[@]}"; do
            [[ "$holder" == "$pid" ]] || others+=("$holder")
        done
    fi
    if [[ "${#others[@]}" -gt 0 ]]; then
        log "GPU ${gpu} is also used by PID ${others[*]}. The launch still targets GPU ${gpu} after PID ${pid} exits."
    fi
        log "Waiting for PID ${pid} on GPU ${gpu}. Checking every ${POLL_SECONDS}s."
    while pid_running "$pid"; do
        log "PID ${pid} is still running."
        sleep "$POLL_SECONDS" || die "sleep rejected POLL_SECONDS='${POLL_SECONDS}'."
    done
    log "PID ${pid} has exited."
else
    require_number "GPU" "$gpu"
    refresh_gpu_state
    if ! uuid="$(uuid_for_index "$gpu")"; then
        die "GPU ${gpu} is not present."
    fi
    log "Waiting until GPU ${gpu} has no compute process. Checking every ${POLL_SECONDS}s."
    while true; do
        refresh_gpu_state
        if ! uuid="$(uuid_for_index "$gpu")"; then
            die "GPU ${gpu} disappeared from nvidia-smi."
        fi
        collect_pids_on_uuid "$uuid"
        if [[ "${#holders[@]}" -eq 0 ]]; then
            break
        fi
        log "GPU ${gpu} is used by PID ${holders[*]}."
        sleep "$POLL_SECONDS" || die "sleep rejected POLL_SECONDS='${POLL_SECONDS}'."
    done
    log "GPU ${gpu} has no compute process."
fi

cd "$ROOT" || exit 1
log "Starting on GPU ${gpu}: pixi run $(quoted_command "$@")"
exec env CUDA_VISIBLE_DEVICES="$gpu" pixi run "$@"
