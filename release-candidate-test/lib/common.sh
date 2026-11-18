# shellcheck shell=bash
# The card's SSH host key changes during the test (pt-os-init replaces keys
# that shipped in the image), so it is not pinned here; rc-check.sh checks it.
SSH_OPTS=(-o ConnectTimeout=10 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
  -o LogLevel=ERROR -o BatchMode=yes)

usage() {
  echo "usage: $0 <pi-top address> stage1|stage2|stage2-only" >&2
  exit 2
}

# stage2-only: a device that missed stage 1 gets everything at once
pref_file() {
  case "$1" in
    stage1) echo stage1.pref ;;
    stage2 | stage2-only) echo stage2.pref ;;
    *) return 1 ;;
  esac
}

remote() {
  # shellcheck disable=SC2029 # the command is meant to expand here
  ssh "${SSH_OPTS[@]}" "pi@$HOST" "$@"
}
