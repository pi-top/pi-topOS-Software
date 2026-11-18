# shellcheck shell=bash
# Runs on the pi-top as root; rc-setup.sh prepends STAGE and PREF.
set -euo pipefail
: "${STAGE:?}" "${PREF:?}"

# Debian's daily run only downloads, but holds the apt lock needed below
if pgrep -af 'unattended-upgrade$|unattended-upgrade ' | grep -- '--download-only' >/dev/null; then
  systemctl stop apt-daily.service
fi

if pgrep -f 'unattended-upgrade$|unattended-upgrade ' >/dev/null; then
  echo "An automatic update is already running; this card no longer starts from" >&2
  echo "the factory state. Restore the image again and set up straight after boot." >&2
  exit 1
fi

add_source() { # repository keyring
  if [ ! -f "/usr/share/keyrings/$2" ]; then
    echo "Missing /usr/share/keyrings/$2 (pi-top-os-archive-keyring)" >&2
    exit 1
  fi
  echo "deb [signed-by=/usr/share/keyrings/$2] https://packages.pi-top.com/$1/debian/ bookworm main" \
    > "/etc/apt/sources.list.d/$(basename "$2" .gpg).list"
}
add_source pi-top-os-unstable pi-top-os-unstable.gpg
add_source experimental pi-top-os-experimental.gpg
printf '%s\n' "$PREF" > /etc/apt/preferences.d/zz-rc-test

state=/var/lib/pt-rc-test/$STAGE
rm -rf "$state"
mkdir -p "$state"
date '+%F %T' > "$state/setup-time"
dpkg-query -W -f='${db:Status-Status} ${Package}:${Architecture} ${Version}\n' |
  awk '$1 == "installed" {print $2, $3}' | sort > "$state/before"
uname -r > "$state/kernel-before"

# Automatic updates run at most once a day; without this, a stage set up on
# the same day as the previous one would not start until tomorrow.
rm -f /var/lib/apt/periodic/*-stamp

apt-get update -qq
plan=$(apt-get -s -o Debug::NoLocking=1 dist-upgrade 2>/dev/null | grep '^Inst ' || true)
echo "$STAGE set up at $(cat "$state/setup-time")."
echo "Planned: $(grep -c . <<<"$plan") packages, of them from pi-top:"
grep -E '\((\S+) (pi-top-os|experimental)' <<<"$plan" | sed 's/^Inst /  /' || echo "  none"
