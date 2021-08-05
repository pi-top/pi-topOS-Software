# pi-topOS Debian Packages Mid-Level Multi-Project Repository

## What?

This is a [meta repo](https://github.com/mateodelnorte/meta), acting as an entry point for all of the OS packaging repositories.

This is included as part of the top-level repository, [pi-topOS-src](https://github.com/pi-top/pi-topOS-src).
It is recommended that you include this meta repository as part of the top-level repository.

## Why?

See [here](https://github.com/mateodelnorte/meta#why-meta) for why meta is a great choice for this. Of particular note is the ability to clone a many-project architecture in one line. This ensures that anyone can get the same copy of all of the files in a standardised way. In addition to this, it is possible to execute arbitrary commands against many repos.

## How?

TL;DR
```
npm i -g meta
meta git clone git@github.com:pi-top/pi-topOS.git
```

### Okay, but how do I work with it?
You can execute scripts from each repository like so:
```shell
meta exec $(pwd)/scripts/update-deb-workflow-files.sh [--parallel]
```

## Packages Still To Make Publicly Available

Require clean-up/rewrite:
* `pt-device-manager`
* `pt-firmware` (Combine `pt-firmware-updater` and `pt-firmware-images` into 1 source repository)

Waiting until Bullseye:
* `pt-display-port` (drop `pt-networking`; move to `pt-os-core`)
* `pt-os-mods`

## Packages To Rename

### Source package renaming
* `pt-device-manager` --> `pi-top-Device-Management`
* `pt-firmware` --> `pi-top-Device-Firmware`
* `pt-further-link` --> `Further-Link`
* `pt-icon-theme` --> `pi-topOS-Icon-Theme`
* `pt-os-core` --> `pi-topOS-Core-Packages`
* `pt-os-mods` --> `pi-topOS-Modifications`
* `pt-plym-splash` --> `pi-topOS-Bootsplash`
* `pt-shutdown-helper` --> `Start-Menu-Shutdown-Helper`
* `pt-sys-oled` --> `pi-top-4-Miniscreen-App`
* `pt-ui-mods` --> `pi-topOS-UI-Modifications`
* `pt-web-portal` --> `pi-topOS-Web-Portal`
* `pt-display-port` --> `pi-top-4-Display-Port`
