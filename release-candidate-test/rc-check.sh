#!/bin/bash
# Pass/fail checks for one stage of the release-candidate test. Run it once the
# update has finished, then again after rebooting for the boot checks.
# Exits 1 if any check fails. Manual checks are in README.md.
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=lib/common.sh
source "$here/lib/common.sh"

[ $# -eq 2 ] || usage
HOST=$1
STAGE=$2
pref_file "$STAGE" >/dev/null || usage

results=$({ printf 'STAGE=%q\n' "$STAGE"; cat "$here/lib/remote-checks.sh"; } | remote 'sudo bash -s')
if [ -z "$results" ]; then
  echo "No results from $HOST" >&2
  exit 1
fi

# Further-Link, as Further's browser reaches it: <ip-with-dashes>.further-link.pi-top.com.
# Further creates that DNS name when it first connects, so go straight to the IP.
if grep -q $'^PASS\trebooted' <<<"$results"; then
  ip=$HOST
  [[ $ip =~ ^[0-9]+(\.[0-9]+){3}$ ]] || ip=$(remote "hostname -I | cut -d' ' -f1")
  name="${ip//./-}.further-link.pi-top.com"
  url="https://$name:8028/status"
  curl() { command curl --resolve "$name:8028:$ip" "$@"; }
  code=$(curl -sS --max-time 15 -o /dev/null -w '%{http_code}' "$url" 2>/dev/null)
  verbose=$(curl -sS -v --max-time 15 -o /dev/null "$url" 2>&1)
  expiry=$(sed -n 's/^\*  *expire date: //p' <<<"$verbose")
  issuer=$(sed -n 's/^\*  *issuer: //p' <<<"$verbose")
  if [ "$code" = 200 ]; then
    results+=$'\n'"PASS"$'\t'"further-link"$'\t'"$url 200, certificate expires $expiry ($issuer)"
  else
    results+=$'\n'"FAIL"$'\t'"further-link"$'\t'"$url returned ${code:-nothing}"
  fi
  # Further-Link 5.13.0 and later switch to the auto-renewed certificate about
  # a minute after starting
  if [ "$STAGE" != stage1 ]; then
    leaf() { awk '/BEGIN CERTIFICATE/ {p = 1} p {print} /END CERTIFICATE/ {exit}' | openssl x509 -outform der | shasum -a 256; }
    served=$(curl -sS --max-time 15 -o /dev/null -w '%{certs}' "$url" | leaf)
    published=$(curl -sS --max-time 15 https://storage.googleapis.com/pi-top-further-link-tls/bundle.pem | leaf)
    if [ "$served" = "$published" ]; then
      results+=$'\n'"PASS"$'\t'"further-link-certificate"$'\t'"serving the published certificate"
    else
      results+=$'\n'"FAIL"$'\t'"further-link-certificate"$'\t'"not serving the published certificate (gs://pi-top-further-link-tls/bundle.pem)"
    fi
  fi
fi

column -t -s $'\t' <<<"$results"
fails=$(grep -c '^FAIL' <<<"$results")
warns=$(grep -c '^WARN' <<<"$results")
echo
echo "$STAGE on $HOST: $(grep -c '^PASS' <<<"$results") passed, $warns warnings, $fails failed"
[ "$fails" -eq 0 ]
