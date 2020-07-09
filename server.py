import os
import sublime

from functools import lru_cache

from .const import ARCH, PLATFORM, PLUGIN_NAME, TEXLAB_VERSION
from LSP.plugin.core.typing import Optional


@lru_cache()
def get_plugin_cache_dir() -> str:
    """
    @brief Get this plugin's cache dir.

    @return The cache dir.
    """

    return os.path.join(sublime.cache_path(), PLUGIN_NAME)


@lru_cache()
def get_server_download_url(
    version: str, arch: str = ARCH, platform: str = PLATFORM,
) -> Optional[str]:
    """
    @brief Get the LSP server download URL.

    @param version  The LSP server version
    @param arch     The arch ("x32" or "x64")
    @param platform The platform ("osx", "linux" or "windows")

    @return The LSP server download URL.
    """

    url_pattern = "https://github.com/latex-lsp/texlab/releases/download/{}/{}"

    if arch == "x64" and platform == "osx":
        tarball_name = "texlab-x86_64-macos.tar.gz"
    elif arch == "x64" and platform == "linux":
        tarball_name = "texlab-x86_64-linux.tar.gz"
    elif arch == "x64" and platform == "windows":
        tarball_name = "texlab-x86_64-windows.zip"
    else:
        return None

    return url_pattern.format(version, tarball_name)


@lru_cache()
def get_server_dir() -> str:
    """
    @brief Get the LSP server dir.

    @return The LSP server dir.
    """

    server_dir = "{}-{}-{}".format(PLATFORM, ARCH, TEXLAB_VERSION)

    return os.path.join(get_plugin_cache_dir(), server_dir)


@lru_cache()
def get_server_bin_path() -> str:
    """
    @brief Get the LSP server binary path.

    @return The LSP server binary path.
    """

    if PLATFORM == "windows":
        binary = "texlab.exe"
    else:
        binary = "texlab"

    return os.path.join(get_server_dir(), binary)


@lru_cache()
def is_plugin_supported() -> bool:
    """
    @brief Determine if plugin can run on this machine.

    @return True if plugin supported, False otherwise.
    """

    return ARCH == "x64" and PLATFORM in ["osx", "linux", "windows"]
