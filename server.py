from __future__ import annotations

from pathlib import Path

import sublime
from lsp_utils import InstallDirectory, UnsupportedPlatformError, download_and_extract, select_platform_asset

from .const import PLATFORM, SERVER_ASSETS, SERVER_BINARY, SERVER_VERSION, SETTINGS_FILENAME


def get_server_asset() -> str | None:
    """Gets the file name of the official pre-built server for the current platform, if there is one."""

    try:
        return select_platform_asset(SERVER_ASSETS)
    except UnsupportedPlatformError:
        return None


def get_server_download_url(version: str, asset: str) -> str | None:
    """
    Gets the LSP server download URL.

    :param      version:  The LSP server version
    :param      asset:    The file name of the release asset
    """

    settings = sublime.load_settings(SETTINGS_FILENAME)
    url = settings.get("lsp_server_download_url", "")

    if not isinstance(url, str) or not url:
        return None

    return url.format_map(
        {
            "version": version,
            "version_without_v": version.lstrip("v"),
            "tarball": asset,
        }
    )


def install_server(storage_dir: Path) -> Path | None:
    """
    Installs the LSP server, unless already installed, and gets the path of its binary.

    :param      storage_dir:  This plugin's storage dir

    :returns:   The path of the server binary or `None` if there is no pre-built server for the current platform.
    """

    asset = get_server_asset()
    if not asset:
        return None
    url = get_server_download_url(SERVER_VERSION, asset)
    if not url:
        return None

    install_dir = InstallDirectory(
        storage_dir,
        "server",
        SERVER_VERSION,
        url,
        # unversioned directories (named "{platform}-{arch}~{version}") used by previous releases
        legacy_dirs=list(storage_dir.glob(f"{PLATFORM}-*~*")),
    )
    server_dir = install_dir.install(
        lambda path: download_and_extract(url, path, filename=asset, executables=[SERVER_BINARY])
    )
    return server_dir / SERVER_BINARY
