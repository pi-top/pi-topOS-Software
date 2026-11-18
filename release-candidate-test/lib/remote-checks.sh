# shellcheck shell=bash
# Runs on the pi-top as root; rc-check.sh prepends STAGE. Prints one
# "RESULT<TAB>check<TAB>detail" line per check, RESULT being PASS, WARN, FAIL or INFO.
set -uo pipefail
: "${STAGE:?}"
export LC_ALL=C

r() { printf '%s\t%s\t%s\n' "$1" "$2" "$3"; }

state=/var/lib/pt-rc-test/$STAGE
if [ ! -f "$state/setup-time" ]; then
  r FAIL setup "rc-setup.sh $STAGE was not run on this card"
  exit 0
fi
since=$(cat "$state/setup-time")
r INFO setup "$STAGE set up at $since"

# --- The update ---------------------------------------------------------------
uu_log=$(awk -v s="$since" '$1 ~ /^[0-9][0-9][0-9][0-9]-/ && $1" "substr($2, 1, 8) >= s' /var/log/unattended-upgrades/unattended-upgrades.log 2>/dev/null)
starts=$(grep -c 'Starting unattended upgrades script' <<<"$uu_log")
killed=$(grep -c 'SIGTERM received' <<<"$uu_log")
finished=$(grep -c 'All upgrades installed' <<<"$uu_log")
errors=$(grep -c ' ERROR ' <<<"$uu_log")
detail="$starts runs, $finished finished, $killed stopped part-way, $errors errors"
if [ "$finished" -eq 0 ]; then
  r FAIL update-finished "$detail"
elif [ "$killed" -gt 0 ] && [ "$STAGE" = stage2 ]; then
  r FAIL update-finished "$detail; stage 2 runs on the new monitor and must finish in one go"
elif [ "$killed" -gt 0 ] && [ "$STAGE" = stage2-only ]; then
  r WARN update-finished "$detail; expected from the factory monitor, as long as a retry finished"
elif [ "$killed" -gt 0 ] || [ "$errors" -gt 0 ]; then
  r WARN update-finished "$detail"
else
  r PASS update-finished "$detail"
fi
[ "$errors" -gt 0 ] && r INFO update-errors "$(grep ' ERROR ' <<<"$uu_log" | head -3 | cut -c1-160 | tr '\n' '|')"

dpkg_log=$(awk -v s="$since" '$1" "$2 >= s' /var/log/dpkg.log 2>/dev/null)
installed=$(grep -c ' status installed ' <<<"$dpkg_log")
first=$(head -1 <<<"$dpkg_log" | cut -c1-19)
last=$(tail -1 <<<"$dpkg_log" | cut -c1-19)
if [ -n "$first" ]; then
  minutes=$(( ($(date -d "$last" +%s) - $(date -d "$first" +%s)) / 60 ))
  r INFO update-time "$installed packages configured, $first to $last ($minutes min)"
fi

audit=$(dpkg --audit 2>&1)
if [ -z "$audit" ] && apt-get check -qq >/dev/null 2>&1; then
  r PASS dpkg-state "dpkg --audit and apt-get check clean"
else
  r FAIL dpkg-state "$(head -3 <<<"$audit" | tr '\n' '|')"
fi

upgradable=$(apt list --upgradable 2>/dev/null | grep upgradable | cut -d/ -f1)
if [ -z "$upgradable" ]; then
  r PASS nothing-left "no upgradable packages"
else
  r WARN nothing-left "$(grep -c . <<<"$upgradable") still upgradable: $(head -8 <<<"$upgradable" | tr '\n' ' ')"
fi

# Packages that were installed at setup and are gone now
pitop_names=$(cat /var/lib/apt/lists/packages.pi-top.com_*_Packages 2>/dev/null | sed -n 's/^Package: //p' | sort -u)
removed=$(join -v1 <(cut -d' ' -f1 "$state/before" | sort) \
  <(dpkg-query -W -f='${db:Status-Status} ${Package}:${Architecture}\n' | awk '$1 == "installed" {print $2}' | sort))
removed_pitop=$(cut -d: -f1 <<<"$removed" | sort -u | comm -12 - <(echo "$pitop_names"))
if [ -n "$removed_pitop" ]; then
  r FAIL pi-top-packages-kept "removed: $(tr '\n' ' ' <<<"$removed_pitop")"
else
  r PASS pi-top-packages-kept "no pi-top package removed"
fi
[ -n "$removed" ] && r INFO removed "$(grep -c . <<<"$removed") removed: $(head -10 <<<"$removed" | tr '\n' ' ')"

# Each exact-version pin in this stage's preferences is installed at that version
while read -r pkg version; do
  now=$(dpkg-query -W -f='${Version}' "$pkg" 2>/dev/null)
  if [ "${now#0:}" = "${version#0:}" ]; then
    r PASS "version:$pkg" "$now"
  else
    r FAIL "version:$pkg" "installed '${now:-none}', expected $version"
  fi
done < <(awk -v RS= '/\nPin: version / && /Pin-Priority: [1-9]/ {
  split($0, l, "\n"); p = ""; v = ""
  for (i in l) { if (l[i] ~ /^Package: /) p = substr(l[i], 10); if (l[i] ~ /^Pin: version /) v = substr(l[i], 14) }
  print p, v }' /etc/apt/preferences.d/zz-rc-test)

# --- Kernel -------------------------------------------------------------------
running=$(uname -r)
flavour=${running#*+rpt-}
meta=linux-image-$flavour
case "$flavour" in rpi-v8 | rpi-2712) meta=$meta:arm64 ;; esac
meta_version=$(dpkg-query -W -f='${Version}' "$meta" 2>/dev/null)
r INFO kernel "running $running (was $(cat "$state/kernel-before")); $meta $meta_version"

if [ "$(dpkg-query -W -f='${db:Status-Status}' pt-os-kernel-pin 2>/dev/null)" = installed ]; then
  if apt-cache policy "$meta" | awk '/^ \*\*\* /{s = 1; next} /^     [^ ]/{s = 0} s' | grep -q 'packages.pi-top.com'; then
    r PASS kernel-approved "$meta $meta_version is the version in pi-top's repositories"
  else
    r FAIL kernel-approved "$meta $meta_version is not in pi-top's repositories"
  fi
  blacklist=$(apt-config dump Unattended-Upgrade::Package-Blacklist | grep -c '::Package-Blacklist:: ')
  if [ "$blacklist" -eq 0 ]; then
    r PASS no-kernel-blacklist "unattended-upgrades has no package blacklist"
  else
    r FAIL no-kernel-blacklist "$blacklist blacklist entries left"
  fi
else
  r FAIL kernel-approved "pt-os-kernel-pin is not installed"
fi

# --- After a reboot -----------------------------------------------------------
booted=$(date -d "$(uptime -s)" +%s)
if [ -z "$last" ] || [ "$booted" -le "$(date -d "$last" +%s)" ]; then
  r WARN rebooted "not rebooted since the update; reboot and run rc-check.sh again for the boot checks"
  exit 0
fi
r PASS rebooted "booted $(uptime -s), after the update"

if [[ "$running" == "$(sed -E 's/^[0-9]+://; s/-.*//' <<<"$meta_version")+rpt-"* ]]; then
  r PASS kernel-booted "booted the installed kernel"
else
  r FAIL kernel-booted "running $running but $meta is $meta_version"
fi

failed=$(systemctl --failed --no-legend --plain | awk '{print $1}')
if [ -z "$failed" ]; then
  r PASS no-failed-units "systemctl --failed is empty"
else
  r FAIL no-failed-units "$(tr '\n' ' ' <<<"$failed")"
fi

for unit in pi-topd pt-miniscreen further-link pt-os-web-portal; do
  if systemctl is-active -q "$unit"; then
    r PASS "active:$unit" "running"
  else
    r FAIL "active:$unit" "$(systemctl is-active "$unit")"
  fi
done

restarts=$(systemctl show -p NRestarts --value pt-miniscreen)
if [ "${restarts:-0}" -eq 0 ]; then
  r PASS miniscreen-restarts "0 since boot"
else
  r WARN miniscreen-restarts "$restarts since boot (bead 3lq)"
fi

if journalctl -b -u pt-firmware-updater --no-pager | grep -q 'firmware is up to date'; then
  r PASS hub-firmware "up to date"
else
  r WARN hub-firmware "$(journalctl -b -u pt-firmware-updater --no-pager | tail -1 | cut -c1-160)"
fi

if devices=$(timeout 30 sudo -u pi pi-top devices 2>&1) && grep -q 'pi-top \[4\]' <<<"$devices"; then
  r PASS hub "$(grep -m1 'pi-top \[4\] (' <<<"$devices")"
else
  r FAIL hub "pi-top devices: $(head -2 <<<"$devices" | tr '\n' ' ')"
fi

if battery=$(timeout 30 sudo -u pi pi-top battery 2>&1) && grep -q '^Capacity: [0-9]' <<<"$battery"; then
  r PASS battery "$(grep '^Capacity' <<<"$battery")%"
else
  r FAIL battery "pi-top battery: $(head -2 <<<"$battery" | tr '\n' ' ')"
fi

errors=$(journalctl -b -p err --no-pager -o cat -u pi-topd -u pt-miniscreen -u further-link \
  -u pt-os-web-portal -u pt-firmware-updater 2>/dev/null)
if [ -z "$errors" ]; then
  r PASS pi-top-errors "no errors logged by pi-top services this boot"
else
  r WARN pi-top-errors "$(grep -c . <<<"$errors") errors: $(head -3 <<<"$errors" | cut -c1-120 | tr '\n' '|')"
fi

start=$(journalctl -b -u apt-daily-upgrade -o short-monotonic --no-pager | grep -m1 'Starting' | sed -E 's/^\[ *([0-9]+)\..*/\1/')
r INFO update-start "${start:-no} automatic update started ${start:+$start s after boot}"

if systemctl cat pt-os-wifi-watchdog.timer >/dev/null 2>&1; then
  if systemctl is-active -q pt-os-wifi-watchdog.timer; then
    r PASS wifi-watchdog "timer active"
  else
    r FAIL wifi-watchdog "timer $(systemctl is-active pt-os-wifi-watchdog.timer)"
  fi
fi

baked=/usr/lib/pt-os-init/baked-ssh-host-keys
for key in /etc/ssh/ssh_host_*_key.pub; do
  fp=$(ssh-keygen -lf "$key" | awk '{print $2}')
  if [ -f "$baked" ] && grep -q -x -F "$fp" "$baked"; then
    r FAIL "ssh-key:$(basename "$key")" "$fp shipped inside a pi-topOS image"
  else
    r PASS "ssh-key:$(basename "$key")" "$fp"
  fi
done
