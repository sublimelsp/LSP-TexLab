import os
import requests
import shutil
import sublime


from .const import PLUGIN_NAME, SETTINGS_FILENAME, TEXLAB_VERSION
from .server import (
    get_plugin_cache_dir,
    get_server_bin_path,
    get_server_dir,
    get_server_download_url,
    is_plugin_supported,
)
from .tarball import decompress
from LSP.plugin import AbstractPlugin
from LSP.plugin.core.protocol import WorkspaceFolder
from LSP.plugin.core.types import ClientConfig
from LSP.plugin.core.typing import List, Tuple, Optional


def plugin_loaded() -> None:
    pass


def plugin_unloaded() -> None:
    pass


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
        cls.download_server_bin()

    @classmethod
    def download_server_bin(cls) -> None:
        """
        @brief Download the LSP server binary.

        @param cls The cls
        """

        server_dir = get_server_dir()
        download_url = get_server_download_url(TEXLAB_VERSION)
        tarball_name = download_url.split("/")[-1]
        tarball_path = os.path.join(server_dir, tarball_name)

        # download the platform-specific LSP server tarball
        response = requests.get(download_url, stream=True)
        with open(tarball_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        decompress(tarball_path, server_dir)

    @classmethod
    def cleanup_cache(cls) -> None:
        """
        @brief Clean up this plugin's cache directory.

        @param cls The cls
        """

        shutil.rmtree(get_plugin_cache_dir(), ignore_errors=True)
        os.makedirs(get_server_dir(), exist_ok=True)
