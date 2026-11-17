#!/bin/bash
# Points a freshly restored factory card at one stage of the release candidate
# and reboots it, so its own Update-Monitor installs the update as a customer's
# would.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=lib/common.sh
source "$here/lib/common.sh"

[ $# -eq 2 ] || usage
HOST=$1
STAGE=$2
pref=$(pref_file "$STAGE") || usage

{
  printf 'STAGE=%q\n' "$STAGE"
  printf 'PREF=%q\n' "$(cat "$here/$pref")"
  cat "$here/lib/remote-setup.sh"
} | remote 'sudo bash -s'

echo "Rebooting $HOST. The update starts 3-15 min after boot with the factory"
echo "Update-Monitor (0.1.0-1), about 1 min with 0.2.0-1 or later."
remote 'sudo systemctl reboot' || true
