from __future__ import annotations

import os

import sublime

from .const import ARCH, PLATFORM, PLATFORM_ARCH_TO_TARBALL, SERVER_VERSION, SETTINGS_FILENAME


def get_server_download_url(version: str, platform: str, arch: str) -> str | None:
    """
    Gets the LSP server download URL.

    :param      version:   The LSP server version
    :param      platform:  The platform ("osx", "linux" or "windows")
    :param      arch:      The arch ("x32", "x64" or "arm64")
    """

    settings = sublime.load_settings(SETTINGS_FILENAME)
    url = settings.get("lsp_server_download_url", "")  # type: str
    tarball = PLATFORM_ARCH_TO_TARBALL.get(f"{platform}_{arch}", "")

    if not (url and tarball):
        return None

    return url.format_map(
        {
            "version": version,
            "version_without_v": version.lstrip("v"),
            "tarball": tarball,
        }
    )


def get_server_dir(storage_dir: str) -> str:
    """
    Gets the server directory.

    :param      storage_dir:  This plugin's storage dir
    """

    server_dir = f"{PLATFORM}-{ARCH}~{SERVER_VERSION}"

    return os.path.join(storage_dir, server_dir)


def get_default_server_bin_path(storage_dir: str) -> str:
    """
    Gets the default LSP server binary path.

    :param      storage_dir:  This plugin's storage dir
    """
    return os.path.join(
        get_server_dir(storage_dir),
        "texlab.exe" if PLATFORM == "windows" else "texlab",
    )
