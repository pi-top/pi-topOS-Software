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

## Packages Still To Add

Debian Packages from other repositories
* [`papirus-folders`](https://github.com/PapirusDevelopmentTeam/papirus-folders)
* [`papirus-icon-theme`](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme)

qtwebengine5 packages (not included in RPi OS due to 'armv7 contamination')
* `libqt5webengine5`
* `libqt5webenginecore5`
* `libqt5webenginewidgets5`
* `qml-module-qtwebengine`
* `qtwebengine5-dev`

Python Packages as Debian Package
* `python3-cbor2`
* `python3-deprecated`
* `python3-dlib`
* `python3-flask-sockets`
* `python3-gevent-websocket`
* `python3-imutils`
* `python3-luma-core`
* `python3-luma-emulator`
* `python3-luma-oled`
* `python3-pycrc`
* `python3-pyftdi`
* `python3-pynput`
* `python3-pyserial`
* `python3-pyusb`
* `python3-pyv4l2camera`
* `python3-pywifi`
* `python3-simple-pid`
* `python3-smbus2`
* `python3-wrapt`

Changes stages for Bullseye
* Update `pt-networking` with  `pt-display-port`
