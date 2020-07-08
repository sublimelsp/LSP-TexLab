import os
import requests
import shutil
import sublime

from functools import lru_cache

from . import tarball
from LSP.plugin import AbstractPlugin
from LSP.plugin.core.protocol import WorkspaceFolder
from LSP.plugin.core.types import ClientConfig
from LSP.plugin.core.typing import List, Tuple, Optional


# @see https://github.com/latex-lsp/texlab/releases
TEXLAB_VERSION = "v2.2.0"

PLUGIN_NAME = "LSP-latex"
SETTINGS_FILENAME = "{}.sublime-settings".format(PLUGIN_NAME)


def plugin_loaded() -> None:
    pass


def plugin_unloaded() -> None:
    pass


@lru_cache()
def get_plugin_cache_dir() -> str:
    """
    @brief Get this plugin's cache dir.

    @return The cache dir.
    """

    return os.path.join(sublime.cache_path(), PLUGIN_NAME)


@lru_cache()
def get_server_download_url(version: str, arch: str, platform: str) -> Optional[str]:
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

    arch = sublime.arch()
    platform = sublime.platform()
    server_dir = "{}-{}-{}".format(platform, arch, TEXLAB_VERSION)

    return os.path.join(get_plugin_cache_dir(), server_dir)


@lru_cache()
def get_server_bin_path() -> str:
    """
    @brief Get the LSP server binary path.

    @return The LSP server binary path.
    """

    platform = sublime.platform()

    if platform == "windows":
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

    arch = sublime.arch()
    platform = sublime.platform()

    return arch == "x64" and platform in ["osx", "linux", "windows"]


class LspLatexPlugin(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return PLUGIN_NAME

    @classmethod
    def configuration(cls) -> Tuple[sublime.Settings, str]:
        settings_path = "Packages/{}/{}".format(PLUGIN_NAME, SETTINGS_FILENAME)
        settings = sublime.load_settings(SETTINGS_FILENAME)

        if not settings.get("command"):
            settings.set("command", [get_server_bin_path()])

        return settings, settings_path

    @classmethod
    def can_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: List[WorkspaceFolder],
        configuration: ClientConfig,
    ) -> Optional[str]:
        if not is_plugin_supported():
            return "Unsupported platform"
        return None

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        return not os.path.isfile(get_server_bin_path())

    @classmethod
    def install_or_update(cls) -> None:
        cls.cleanup_cache()

        server_dir = get_server_dir()
        download_url = get_server_download_url(TEXLAB_VERSION, sublime.arch(), sublime.platform())
        tarball_name = download_url.split("/")[-1]
        tarball_path = os.path.join(server_dir, tarball_name)

        response = requests.get(download_url, stream=True)
        with open(tarball_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        tarball.decompress(tarball_path, server_dir)

    @classmethod
    def cleanup_cache(cls) -> None:
        """
        @brief Clean up this plugin's cache directory.

        @param cls The cls
        """

        shutil.rmtree(get_plugin_cache_dir(), ignore_errors=True)
        os.makedirs(get_server_dir(), exist_ok=True)
