PackageCloud CLI
================

CLI to manage PackageCloud repositories, using the their `Web API <https://packagecloud.io/docs/api>`_ .

Installation
------------

Install locally running pip in the :code:`package-cloud-cli` folder:

.. code-block::

  $ cd pi-topOS-Software/scripts/package-cloud-cli
  $ sudo -H pip3 install .

This will install the :code:`package_cloud_cli` python package and the :code:`package-cloud` CLI tool into your machine.

Usage
-----

.. code-block::

  $ package-cloud [OPTIONS] REPO USER DISTRO DISTRO_VERSION API_TOKEN

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
    --all-packages                  Queries all packages in the repository.
    --package-name TEXT             Specify a particular package to target.
    --cleanup-and-keep INTEGER      Remove old versions of a package and keep
                                    the specified number of versions.
    -v, --verbosity [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                    Verbosity level.
    --dry-run                       Perform a dry-run without destroying or
                                    modifying any package.
    -a, --additional-repo TEXT      Specify an aditional repository to look for
                                    packages.
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

  $ package-cloud --all-packages
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


- Cleanup old versions of one package

The :code:`--cleanup-and-keep` option tells the CLI to cleanup old versions of a package, leaving at least the specified number of versions of the package in the repository.

.. code-block:: bash

  $ package-cloud --package-name pi-topd  --cleanup-and-keep 2
  Package: pi-topd (7 versions), latest: 5.3.1-1
  Versions: [5.1.0-2, 5.1.0-3, 5.1.0-4, 5.1.0-5, 5.2.0-1, 5.2.1-1, 5.3.1-1]
  Deleting old versions: will delete 5 and leave 2
     Deleting: 5.1.0-2
     Deleting: 5.1.0-3
     Deleting: 5.1.0-4
     Deleting: 5.1.0-5
     Deleting: 5.2.0-1
  Kept versions: [5.2.1-1, 5.3.1-1]

- Cleanup old versions of all packages

.. code-block:: bash

  $ package-cloud --all-packages --cleanup-and-keep 2

  Package: usb-eth-gadget (2 versions), latest: 1.1.4-3
  Versions: [1.1.4-2, 1.1.4-3]
  Deleting old versions: will delete 0 and leave 2
  Kept versions: [1.1.4-2, 1.1.4-3]

  Package: web-renderer (2 versions), latest: 5.0.0-1
  Versions: [4.1.1-1, 5.0.0-1]
  Deleting old versions: will delete 0 and leave 2
  Kept versions: [4.1.1-1, 5.0.0-1]

  Package: web-renderer-dbgsym (2 versions), latest: 5.0.0-1
  Versions: [4.1.1-1, 5.0.0-1]
  Deleting old versions: will delete 0 and leave 2
  Kept versions: [4.1.1-1, 5.0.0-1]

  Package: wifi-ap-sta (6 versions), latest: 0.7.3-1
  Versions: [0.5.0-1, 0.5.0-2, 0.6.0-1, 0.7.1-1, 0.7.2-1, 0.7.3-1]
  Deleting old versions: will delete 4 and leave 2
     Deleting: 0.5.0-1
     Deleting: 0.5.0-2
     Deleting: 0.6.0-1
     Deleting: 0.7.1-1
  Kept versions: [0.7.2-1, 0.7.3-1]

- Include other repositories and check for promotions

Using the :code:`--additional-repo` flag you can include more repositories in the query. This flag will also let you know if it's
possible to promote the specified package from the repository set as positional argument (or via the environment variable :code:`PC_REPO`) to
the additional repository specfied with :code:`--additional-repo`.

.. code-block:: bash

  $ PC_REPO=pi-top-os-unstable package-cloud --package-name pi-topd --additional-repo pi-top-os
  Package: pi-topd (1 versions), latest: 5.3.1-2
  Versions (pi-top-os-unstable): [5.3.1-2]
  Versions (pi-top-os): [5.1.0-2, 5.1.0-3, 5.1.0-4, 5.1.0-5, 5.2.0-1, 5.2.1-1, 5.3.1-1]

  Package 'pi-topd' can be promoted from 'pi-top-os-unstable' (5.3.1-2) to 'pi-top-os' (Latest version is '5.3.1-1')"


.. code-block:: bash

  $ PC_REPO=pi-top-os-unstable package-cloud --package-name web-renderer --additional-repo pi-top-os

  Package: web-renderer (1 versions), latest: 0.5-1
  Versions (pi-top-os-unstable): [0.5-1]

  Package 'web-renderer' can be promoted from 'pi-top-os-unstable' (0.5-1) to 'pi-top-os' (Package doesn't exist in pi-top-os)
