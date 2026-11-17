# Release-candidate test

Run before promoting anything from `pi-top-os-unstable` to `pi-top-os`. It shows that a customer's pi-top, starting from the factory image, updates cleanly to the release by itself and still works afterwards.

The test card plays a customer device: `rc-setup.sh` makes the packages being promoted look already promoted, then the card's own Update-Monitor installs them on boot. `rc-check.sh` checks the result, and the manual checks below cover what a script can't see.

## Stages

This release goes out in two promotions, so the test has two stages on the same card:

| Stage | Promoted | Why |
|---|---|---|
| `stage1` | Update-Monitor 0.2.1-1 only | The factory monitor (0.1.0-1) stops part-way when pi-topd restarts. Field devices get the fixed monitor first. |
| `stage2` | Everything else in unstable, plus the third-party rebuilds | Installed by the fixed monitor, in one go |
| `stage2-only` (optional) | Same as stage 2, on a fresh card | A device that was off during stage 1. The update may stop part-way once, then must finish on a retry. |

`stage1.pref` and `stage2.pref` say exactly what is promoted in each stage. Update them for each release: the third-party rebuilds in `experimental` are pinned by exact version, because the highest version there can be an old build. A release with a single promotion needs only `stage2`.

## Before you start

- A Mac with an SSH key, and the pi-top [4] on its charger.
- The factory image, `pi-topOS-4.0-factory-2025-07-11.img.gz`, and a spare SD card.
- Wi-Fi the pi-top can join.

## Checklist

### Stage 1

1. Write the factory image to the SD card (Raspberry Pi Imager, "Use custom").
2. Boot the pi-top from it. Get it online and reachable over SSH: Wi-Fi through onboarding, or over the USB cable at `192.168.64.1` with `sudo nmcli device wifi connect <SSID> password <password>`. Then `ssh-copy-id pi@<address>`.
3. **Straight away**, before the factory monitor starts its own update (3–15 min after boot):
   `./rc-setup.sh <address> stage1`
   It lists what will be installed, then reboots the pi-top. The update starts by itself after the reboot.
4. Wait for the update. With Raspberry Pi OS updates included it takes about 1½–2 hours. To follow it:
   `ssh pi@<address> sudo tail -f /var/log/unattended-upgrades/unattended-upgrades.log`
   It is done at `All upgrades installed`.
5. `./rc-check.sh <address> stage1`. It asks for a reboot: `ssh pi@<address> sudo reboot`, wait 3 minutes, and run it again.
6. Do the manual checks.

### Stage 2

7. `./rc-setup.sh <address> stage2` on the same card, then repeat steps 4–6 with `stage2`.

### Optional: device that missed stage 1

8. Restore the factory image again and repeat steps 2–6 with `stage2-only`.

Expect a SSH host key warning on the Mac during the test: updating replaces host keys that shipped inside the image. The scripts don't pin the key, and `rc-check.sh` checks the new one.

## What rc-check.sh checks

After the update:

- The update finished. In `stage2` it must finish in one run.
- dpkg and apt are consistent, and nothing is left to upgrade.
- No pi-top package was removed.
- Every exact-version pin in the stage's `.pref` is installed at that version.
- From stage 2: `pt-os-kernel-pin` is installed, the kernel is the version in pi-top's repositories, and unattended-upgrades has no blacklist.

After the reboot:

- The pi-top booted the installed kernel.
- No failed systemd units.
- pi-topd, the miniscreen, Further-Link and the web portal are running. A miniscreen restart is a warning (bead `3lq`).
- Hub firmware is up to date, and `pi-top devices` and `pi-top battery` answer.
- Errors logged by pi-top services are warnings.
- How soon after boot the automatic update started.
- The Wi-Fi watchdog timer is active.
- The SSH host keys are not ones that shipped in an image.
- From the Mac: Further-Link answers on `https://<ip-with-dashes>.further-link.pi-top.com:8028` with a trusted certificate, and when it expires.

`FAIL` blocks the release. `WARN` needs a look and a note in the record. The exit code is 1 if anything failed.

## Manual checks

After each stage's reboot:

- [ ] **Miniscreen** shows the menu; the buttons move between pages; the battery page shows the charge.
- [ ] **Desktop** appears on the pi-top display; the keyboard and trackpad work.
- [ ] **Sound** plays through the speaker.
- [ ] **Further over Wi-Fi**: on further.pi-top.com, connect to this pi-top and run a Python program that prints. The output appears.
- [ ] **Web portal**: `http://<address>` opens the pi-top landing page, and the web desktop (VNC) loads.
- [ ] **Power button**: a press shuts the pi-top down cleanly; a press turns it back on and it boots normally.

## Record

Add a row to the release record for each stage: the date, the stage, the `rc-check.sh` summary line with any `WARN`/`FAIL` lines, the manual checks, and the update time it reports.
