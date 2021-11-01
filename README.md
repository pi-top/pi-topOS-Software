# pi-topOS Software

This is a [meta repo](https://github.com/mateodelnorte/meta) which provides a convenient way to work with the many-project architecture of pi-topOS.

This is also where [Issues](i-top/pi-topOS-Software/issues) are filed where it cannot be placed in a specific software package.

## Quick Start

- [Install npm](https://docs.npmjs.com/cli/v7/configuring-npm/install#using-a-node-version-manager-to-install-nodejs-and-npm)

- Install [meta](https://github.com/mateodelnorte/meta):

```
npm i -g meta
```

- Clone this repository and all child repos:

```
meta git clone git@github.com:pi-top/pi-topOS-Software.git
```

## Working with multiple repositories

It is possible to run commands on this repo and all of the child repos:

```shell
meta exec "git status" [--parallel]
meta exec /path/to/script.sh [--parallel]
```

However, it is sometimes desirable to work with a group of repos. This is where `pt-os-meta-exec` comes in...

### Advanced usage

`pt-os-meta-exec` is a tool that has been developed to simplify bulk-edits across the pi-topOS software codebase.

Installation:

```
cd scripts/pt-os-meta-exec
pip3 install -e .
```

For usage:

```
pt-os-meta-exec --help
```

Usage: `pt-os-meta-exec [OPTIONS] [COMMAND]...`

If no command is provided, then an interactive CLI prompt is provided.

Quick Examples:

```
pt-os-meta-exec \
  --condition-file "debian/*" \
  --parallel \
  --strict \
  --debug

pt-os-meta-exec \
  --condition-no-file "debian/*"
  "git status"

pt-os-meta-exec \
  --condition "grep -q 'native' debian/source/format"

pt-os-meta-exec \
  --repo-match "pi-top-4-Miniscreen" \
  --repo-match "pi-top-Firmware-Updater" \
  --dry-run
```
