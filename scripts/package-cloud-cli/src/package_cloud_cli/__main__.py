"""Command-line interface for working with Package Cloud repositories."""
import logging

import click
import click_logging

from .classes import PackageCloudManager, PackageCloudRepoConfiguration

logger = logging.getLogger(__name__)

click_logging.basic_config(logger)
logging.getLogger("urllib3").setLevel(logging.INFO)


@click.command()
@click.argument("repo", envvar="PC_REPO")
@click.argument("user", envvar="PC_USER")
@click.argument("distro", envvar="PC_DISTRO")
@click.argument("distro_version", envvar="PC_DISTRO_VERSION")
@click.argument("api_token", envvar="PC_API_TOKEN")
@click.option(
    "--list-packages", is_flag=True, help="Lists all packages in the repository."
)
@click.option("--package-name", type=str, help="Package to look for.")
@click.option("--cleanup", is_flag=True)
@click.option(
    "--versions_to_keep",
    type=int,
    default=10,
    help="Maximum number of versions of a package to keep in the repository. Defaults to 10.",
)
@click.option(
    "-v",
    "--verbosity",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="INFO",
    help="Verbosity level.",
)
def main(
    repo,
    user,
    distro,
    distro_version,
    api_token,
    list_packages,
    package_name,
    cleanup,
    versions_to_keep,
    verbosity,
):
    """
    REPO: Name of the PackageCloud repository. Can be passed through environment variable 'PC_REPO'

    USER: Username. Can be passed through environment variable 'PC_USER'

    DISTRO: Distribution of the repository . Can be passed through environment variable 'PC_DISTRO'

    DISTRO_VERSION: Version of the distribution of the repository. Can be passed through environment variable 'PC_DISTRO_VERSION'

    API_TOKEN: PackageCloud API token. Can be passed through environment variable 'PC_API_TOKEN'
    """
    logging.basicConfig(level=getattr(logging, verbosity))

    logging.debug(f"Checking '{user}/{repo}' for distro '{distro}/{distro_version}'")

    manager = PackageCloudManager(
        PackageCloudRepoConfiguration(
            api_token=api_token,
            repository=repo,
            user=user,
            distribution=distro,
            distribution_version=distro_version,
        )
    )

    packages = []
    if package_name:
        package = manager.get_package(package_name)
        packages.append(package)
    elif list_packages:
        packages = manager.list_packages()

    for package in packages:
        versions = manager.package_versions(package)
        versions.sort()

        print(
            f"Package: {package.name} ({package.versions_count} versions), latest: {versions[-1].version_str}"
        )
        print(f"Versions: {versions}")

        if cleanup:
            try:
                manager.delete_old_versions(versions=versions, keep=versions_to_keep)
            except Exception as e:
                logger.error(f"{e}")

        print()


if __name__ == "__main__":
    main(prog_name="package-cloud-cli")  # pragma: no cover
