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
