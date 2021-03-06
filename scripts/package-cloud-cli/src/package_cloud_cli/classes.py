"""Command-line interface for working with Package Cloud repositories."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, List, Optional

import requests
from linkheader_parser import parse
from packaging import version

logger = logging.getLogger(__name__)


@dataclass
class PackageCloudRepoConfiguration:
    api_token: str
    repository: str
    user: str
    distribution: str
    distribution_version: str

    @property
    def base(self):
        return f"https://{self.api_token}:@packagecloud.io/"

    @property
    def base_url(self):
        return f"{self.base}/api/v1/repos/{self.user}/{self.repository}"

    @property
    def packages_url(self):
        return f"{self.base_url}/packages/deb.json"


@dataclass
class PackageVersion:
    # From https://packagecloud.io/docs/api#object_PackageVersion
    name: str
    versions_count: int
    versions_url: str
    repository_url: str
    repository_html_url: str

    def __repr__(self):
        return f"{self.name}"


@dataclass(order=True)
class PackageFragment:
    # From https://packagecloud.io/docs/api#object_PackageFragment
    name: str  # The name of the package.
    created_at: str  # When the package was uploaded.
    distro_version: str  # The distro_version for the package.
    version: str  # The version of the package.
    release: str  # The release of the package (if available).
    epoch: str  # The epoch of the package (if available).
    scope: str  # The scope of the package (if available).
    private: str  # Whether or not the package is in a private repository.
    type: str  # The type of package ("deb", "gem", or "rpm").
    filename: str  # The filename of the package.
    uploader_name: str  # The name of the uploader for the package.
    indexed: str  # Whether or not this package has been indexed.
    repository_html_url: str  # The HTML url of the repository.
    package_url: str  # The API url for this package.
    package_html_url: str  # The HTML url for this package.
    downloads_detail_url: str  # The url to get access log details for package downloads.
    downloads_series_url: str  # The url to get time series data for package downloads.
    downloads_count_url: str  # The url to get the total number of package downloads.
    promote_url: str  # The url for promoting this to another repository.
    destroy_url: str  # The url for the HTTP DELETE request to destroy this package.
    # Not in documentation:
    sha256sum: str
    download_url: str

    sort_index: int = field(init=False, repr=False)

    def __post_init__(self):
        self.sort_index = version.parse(self.version_str)

    @property
    def version_str(self):
        v = self.version
        if self.release:
            v += f"-{self.release}"
        return v

    def __repr__(self):
        return f"{self.version_str}"


class RequestType(Enum):
    GET = auto()
    POST = auto()
    DELETE = auto()
    PUT = auto()


class PackageCloudManager:
    def __init__(self, config: PackageCloudRepoConfiguration) -> None:
        self.config = config

    def _send_request(
        self, url: str, request_type: RequestType, callback: Optional[Callable]
    ) -> None:
        def format_url(url):
            if url.startswith("/"):
                url = self.config.base + url
            if self.config.api_token in url:
                return url
            u = url.split("https://")
            return f"https://{self.config.api_token}:@{u[1]}"

        url = format_url(url)

        logger.debug(
            f"send_request: {request_type.name} - {url.replace(self.config.api_token, '*********')}"
        )

        if request_type == RequestType.GET:
            request_response = requests.get(url)
            if request_response.status_code != 200:
                raise Exception(f"{request_response.text}")

            # Responses might have headers for pagination
            # See https://packagecloud.io/docs/api#pagination
            if hasattr(request_response, "headers") and request_response.headers.get(
                "Link"
            ):
                link = parse(request_response.headers["Link"])
                if link.get("next") and link["next"].get("url"):
                    self._send_request(
                        url=link["next"]["url"],
                        request_type=RequestType.GET,
                        callback=callback,
                    )

        elif request_type == RequestType.DELETE:
            request_response = requests.delete(url)
            if request_response.status_code != 200:
                raise Exception(f"{request_response.text}")

        else:
            raise NotImplementedError

        if callable(callback):
            callback(request_response.json())

    ##############
    # Public API #
    ##############

    def list_packages(self) -> List[PackageVersion]:
        packages = []

        def parse_packages_response(response):
            for package in response:
                packages.append(PackageVersion(**package))

        self._send_request(
            self.config.packages_url,
            request_type=RequestType.GET,
            callback=parse_packages_response,
        )
        return packages

    def get_package(self, package_name: str) -> Optional[PackageVersion]:
        for package_obj in self.list_packages():
            if package_obj.name == package_name:
                return package_obj
        return None

    def package_versions(self, package: PackageVersion) -> List[PackageFragment]:
        versions = []

        def parse_versions(response):
            for version_response in response:
                versions.append(PackageFragment(**version_response))

        self._send_request(
            package.versions_url, request_type=RequestType.GET, callback=parse_versions
        )
        return versions

    def package_latest_version(
        self, package: PackageVersion
    ) -> Optional[PackageFragment]:
        latest = None
        for candidate in self.package_versions(package):
            if latest is None or candidate > latest:
                latest = candidate
        return latest

    def delete_old_versions(
        self, versions: List[PackageFragment], keep: int, dry_run: bool = False
    ) -> None:
        def find_duplicates(versions: List[PackageFragment]) -> List[str]:
            seen = set()
            duplicates = []

            for version_obj in versions:
                version_str = version_obj.version_str

                # Remove 'snapshot' substring
                version_str = version_str.split(".gbp")[0]

                if version_str in seen:
                    duplicates.append(version_str)
                else:
                    seen.add(version_str)
            return duplicates

        duplicates = find_duplicates(versions)
        if len(duplicates) > 0:
            raise Exception(
                f"Duplicated versions found. Fix this issue manually and try again: {duplicates}"
            )

        versions_to_keep = min(keep, len(versions))
        versions_to_delete = len(versions) - versions_to_keep

        print(
            f"Deleting old versions: will delete {versions_to_delete} and leave {versions_to_keep}"
        )
        for version_obj in versions[0:versions_to_delete]:
            print(f"\tDeleting: {version_obj.version_str}")
            if dry_run:
                continue
            try:
                self._send_request(
                    url=version_obj.destroy_url,
                    request_type=RequestType.DELETE,
                    callback=None,
                )
            except Exception as e:
                logger.error(
                    f"Error deleting {version_obj.name} {version_obj.version_str}': {e}"
                )

        print(f"Kept versions: {versions[versions_to_delete:]}")
