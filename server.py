from .const import ARCH
from .const import PLATFORM
from .const import PLUGIN_NAME
from .const import SERVER_VERSION
from .const import SETTINGS_FILENAME
from functools import lru_cache
from LSP.plugin.core.typing import Optional
import os
import sublime


@lru_cache()
def get_plugin_storage_dir() -> str:
    """ Gets this plugin's storage dir. """

    return os.path.abspath(os.path.join(sublime.cache_path(), "..", "Package Storage", PLUGIN_NAME))


@lru_cache()
def get_server_download_url(version: str, arch: str, platform: str) -> Optional[str]:
    """
    Gets the LSP server download URL.

    :param      version:   The LSP server version
    :param      arch:      The arch ("x32" or "x64")
    :param      platform:  The platform ("osx", "linux" or "windows")
    """

    settings = sublime.load_settings(SETTINGS_FILENAME)
    url = str(settings.get("lsp_server_download_url", ""))

    if arch == "x64" and platform == "osx":
        tarball = "texlab-x86_64-macos.tar.gz"
    elif arch == "x64" and platform == "linux":
        tarball = "texlab-x86_64-linux.tar.gz"
    elif arch == "x64" and platform == "windows":
        tarball = "texlab-x86_64-windows.zip"
    else:
        tarball = ""

    if not url or not tarball:
        return None

    return url.format_map({"version": version, "tarball": tarball})


@lru_cache()
def get_server_dir() -> str:
    """ Gets the server directory. """

    server_dir = "{}-{}~{}".format(PLATFORM, ARCH, SERVER_VERSION)

    return os.path.join(get_plugin_storage_dir(), server_dir)


@lru_cache()
def get_server_bin_path() -> str:
    """ Gets the LSP server binary path. """

    return os.path.join(
        get_server_dir(),
        "texlab.exe" if PLATFORM == "windows" else "texlab",
    )
