"""Command-line interface for working with Package Cloud repositories."""
import logging

import click
import click_logging
from packaging import version

from .classes import PackageCloudManager, PackageCloudRepoConfiguration

logger = logging.getLogger(__name__)

click_logging.basic_config(logger)
logging.getLogger("urllib3").setLevel(logging.INFO)


@click.command()
@click.argument("repo", envvar="PC_REPO")
@click.argument("user", envvar="PC_USER")
@click.argument("distro", envvar="PC_DISTRO")
@click.argument("distro-version", envvar="PC_DISTRO_VERSION")
@click.argument("api_token", envvar="PC_API_TOKEN")
@click.option(
    "--all-packages", is_flag=True, help="Queries all packages in the repository."
)
@click.option(
    "--package-name", type=str, help="Specify a particular package to target."
)
@click.option(
    "--cleanup-and-keep",
    type=int,
    help="Remove old versions of a package and keep the specified number of versions.",
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
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a dry-run without destroying or modifying any package.",
)
@click.option(
    "-a",
    "--additional-repo",
    multiple=True,
    help="Specify an aditional repository to look for packages.",
    default=[],
)
def main(
    repo,
    user,
    distro,
    distro_version,
    api_token,
    all_packages,
    package_name,
    cleanup_and_keep,
    verbosity,
    dry_run,
    additional_repo,
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

    config = PackageCloudRepoConfiguration(
        api_token=api_token,
        repository=repo,
        user=user,
        distribution=distro,
        distribution_version=distro_version,
    )
    manager = PackageCloudManager(config)

    packages = []
    if package_name:
        package = manager.get_package(package_name)
        if package:
            packages.append(package)
        else:
            print(f"Package '{package_name}' not found in '{repo}'.")
    elif all_packages:
        packages = manager.list_packages()

    for package in packages:
        versions = manager.package_versions(package)
        versions.sort()

        print(
            f"Package: {package.name} ({package.versions_count} versions), latest: {versions[-1].version_str}"
        )
        print(f"Versions ({repo}): {versions}")

        try:
            for other_repo in additional_repo:
                manager.config.repository = other_repo
                package_in_other_repo = manager.get_package(package.name)
                if package_in_other_repo:
                    other_versions = manager.package_versions(
                        package=package_in_other_repo
                    )
                    other_versions.sort()
                    print(f"Versions ({other_repo}): {other_versions}")

                    if version.parse(other_versions[-1].version_str) < version.parse(
                        versions[-1].version_str
                    ):
                        print(
                            f"\nPackage '{package.name}' can be promoted from '{repo}' ({versions[-1].version_str}) "
                            f"to '{other_repo}' (Latest version is '{other_versions[-1].version_str})')"
                        )
                else:
                    print(
                        f"\nPackage '{package.name}' can be promoted from '{repo}' ({versions[-1].version_str}) "
                        f"to '{other_repo}' (Package doesn't exist in {other_repo})"
                    )
        except Exception as e:
            logger.error(f"{e}")
        finally:
            manager.config.repository = repo

        if cleanup_and_keep:
            try:
                manager.delete_old_versions(
                    versions=versions, keep=cleanup_and_keep, dry_run=dry_run
                )
            except Exception as e:
                logger.error(f"Cleanup error: {e}")

        print()


if __name__ == "__main__":
    main(prog_name="package-cloud-cli")  # pragma: no cover
