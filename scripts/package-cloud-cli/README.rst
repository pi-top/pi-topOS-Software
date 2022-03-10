PackageCloud CLI
================

CLI to manage PackageCloud repositories.

Usage
-----

.. code-block::

  $ package-cloud --help
  Usage: package-cloud [OPTIONS] REPO USER DISTRO DISTRO_VERSION API_TOKEN

    REPO: Name of the PackageCloud repository. Can be passed through environment
    variable 'PC_REPO'

    USER: Username. Can be passed through environment variable 'PC_USER'

    DISTRO: Distribution of the repository . Can be passed through environment
    variable 'PC_DISTRO'

    DISTRO_VERSION: Version of the distribution of the repository. Can be passed
    through environment variable 'PC_DISTRO_VERSION'

    API_TOKEN: PackageCloud API token. Can be passed through environment
    variable 'PC_API_TOKEN'

  Options:
    --list-packages                 Lists all packages in the repository.
    --package-name TEXT             Package to look for.
    --cleanup
    --versions_to_keep INTEGER      Maximum number of versions of a package to
                                    keep in the repository. Defaults to 10.
    -v, --verbosity [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                    Verbosity level.
    --help                          Show this message and exit.



Example
-------

- Get information about a particular package

.. code-block:: bash

  $ package-cloud pi-top-os pi-top debian bullseye <PACKAGE_CLOUD_API_TOKEN> --package-name pi-topd

  Package: pi-topd (7 versions), latest: 5.3.1-1
  Versions: [5.1.0-2, 5.1.0-3, 5.1.0-4, 5.1.0-5, 5.2.0-1, 5.2.1-1, 5.3.1-1]


- Using environment variables

Instead of providing the repository information explicitly, these values can be passed using environment variables. For example, the previous example would be:

.. code-block:: bash

  $ PC_USER=pi-top \
    PC_DISTRO=debian \
    PC_DISTRO_VERSION=bullseye \
    PC_API_TOKEN=<PACKAGE_CLOUD_API_TOKEN> \
    package-cloud --package-name pi-topd

  Package: pi-topd (7 versions), latest: 5.3.1-1
  Versions: [5.1.0-2, 5.1.0-3, 5.1.0-4, 5.1.0-5, 5.2.0-1, 5.2.1-1, 5.3.1-1]

- List all packages in a repository

  Assuming that the environment variables :code:`PC_USER`, :code:`PC_DISTRO`, :code:`PC_DISTRO_VERSION` and :code:`PC_API_TOKEN` are set:

.. code-block:: bash

  $ package-cloud --list-packages
  Package: usb-eth-gadget (2 versions), latest: 1.1.4-3
  Versions: [1.1.4-2, 1.1.4-3]

  Package: web-renderer (2 versions), latest: 5.0.0-1
  Versions: [4.1.1-1, 5.0.0-1]

  Package: web-renderer-dbgsym (2 versions), latest: 5.0.0-1
  Versions: [4.1.1-1, 5.0.0-1]

  Package: wifi-ap-sta (6 versions), latest: 0.7.3-1
  Versions: [0.5.0-1, 0.5.0-2, 0.6.0-1, 0.7.1-1, 0.7.2-1, 0.7.3-1]

  Package: pt-os-init (9 versions), latest: 5.5.0-2
  Versions: [5.0.1-1, 5.0.1-2, 5.2.0-1, 5.3.0-2, 5.4.0-1, 5.4.0-2, 5.4.0-3, 5.5.0-1, 5.5.0-2]

  Package: pt-os-lite (5 versions), latest: 5.5.0-2
  Versions: [5.4.0-1, 5.4.0-2, 5.4.0-3, 5.5.0-1, 5.5.0-2]

  Package: pt-os-net-mods (2 versions), latest: 1.0.1-2
  Versions: [1.0.1-1, 1.0.1-2]

  Package: pt-os-networking (7 versions), latest: 5.5.0-2
  Versions: [5.2.0-1, 5.3.0-2, 5.4.0-1, 5.4.0-2, 5.4.0-3, 5.5.0-1, 5.5.0-2]

  Package: pt-os-notify-services (9 versions), latest: 5.5.0-2
  Versions: [5.0.1-1, 5.0.1-2, 5.2.0-1, 5.3.0-2, 5.4.0-1, 5.4.0-2, 5.4.0-3, 5.5.0-1, 5.5.0-2]


- Cleanup old versions of packages

The :code:`--cleanup` flag tells the CLI to cleanup old versions of a package. By default, it will keep 10 versions of a package in the repository.
The :code:`--versions-to-keep` flag overrides this value.

.. code-block:: bash

  $ package-cloud --package-name pi-topd  --cleanup --versions-to-keep 2
  Package: pi-topd (7 versions), latest: 5.3.1-1
  Versions: [5.1.0-2, 5.1.0-3, 5.1.0-4, 5.1.0-5, 5.2.0-1, 5.2.1-1, 5.3.1-1]
  Deleting old versions: will delete 5 and leave 2
  Deleting: 5.1.0-2
  Deleting: 5.1.0-3
  Deleting: 5.1.0-4
  Deleting: 5.1.0-5
  Deleting: 5.2.0-1
  Kept versions: [5.2.1-1, 5.3.1-1]
