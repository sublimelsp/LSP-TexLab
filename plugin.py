from .const import ARCH
from .const import PLATFORM
from .const import PLUGIN_NAME
from .const import SERVER_VERSION
from .const import SETTINGS_FILENAME
from .server import get_plugin_storage_dir
from .server import get_server_bin_path
from .server import get_server_dir
from .server import get_server_download_url
from .tarball import decompress, download
from LSP.plugin import AbstractPlugin, Request
from LSP.plugin.core.registry import LspTextCommand
from LSP.plugin.core.protocol import WorkspaceFolder
from LSP.plugin.core.types import ClientConfig
from LSP.plugin.core.typing import Any, List, Tuple, Optional
from LSP.plugin.core.views import text_document_identifier, text_document_position_params
import os
import shutil
import sublime


class LspTexLabPlugin(AbstractPlugin):
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
        try:
            if not (ARCH == "x64" and PLATFORM in ["osx", "linux", "windows"]):
                raise RuntimeError("Only supports OSX/Linux/Windows x64 system.")
        except Exception as e:
            return "{}: {}".format(PLUGIN_NAME, e)

        return None

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        return not os.path.isfile(get_server_bin_path())

    @classmethod
    def install_or_update(cls) -> None:
        cls._cleanup_cache()
        cls._prepare_server_bin()

    @classmethod
    def _prepare_server_bin(cls) -> None:
        """Download the LSP server binary."""

        server_dir = get_server_dir()
        download_url = get_server_download_url(SERVER_VERSION, ARCH, PLATFORM)
        tarball_name = download_url.split("/")[-1]
        tarball_path = os.path.join(server_dir, tarball_name)

        if not download_url:
            raise RuntimeError("Unsupported platform...")

        download(download_url, tarball_path)
        decompress(tarball_path, server_dir)

    @classmethod
    def _cleanup_cache(cls) -> None:
        """Clean up this plugin's cache directory."""

        shutil.rmtree(get_plugin_storage_dir(), ignore_errors=True)


class LspTexlabForwardSearchCommand(LspTextCommand):

    session_name = PLUGIN_NAME

    def run(self, edit: sublime.Edit) -> None:
        session = self.session_by_name(PLUGIN_NAME)
        if not session:
            return
        params = text_document_position_params(self.view, next(iter(self.view.sel())).a)
        session.send_request(Request("textDocument/forwardSearch", params), self.on_response_async, self.on_error_async)

    def on_response_async(self, response: Any) -> None:
        status = response["status"]
        window = self.view.window()
        if window is None:
            return
        if status == 0:
            pass  # success
        elif status == 1:
            window.status_message(PLUGIN_NAME + ": Previewer exited with errors")
        elif status == 2:
            window.status_message(PLUGIN_NAME + ": Previewer failed to start or crashed")
        elif status == 3:
            window.status_message(PLUGIN_NAME + ": Previewer is not configured")

    def on_error_async(self, error: Any) -> None:
        pass


class LspTexlabBuildCommand(LspTextCommand):

    session_name = PLUGIN_NAME

    def run(self, edit: sublime.Edit) -> None:
        session = self.session_by_name(PLUGIN_NAME)
        if not session:
            return
        params = {"textDocument": text_document_identifier(self.view)}
        session.send_request(Request("textDocument/build", params), self.on_response_async, self.on_error_async)

    def on_response_async(self, response: Any) -> None:
        status = response["status"]
        window = self.view.window()
        if window is None:
            return
        if status == 0:
            pass  # success
        elif status == 1:
            window.status_message(PLUGIN_NAME + ": Build error")
        elif status == 2:
            window.status_message(PLUGIN_NAME + ": Build failure")
        elif status == 3:
            window.status_message(PLUGIN_NAME + ": Build cancelled")

    def on_error_async(self, error: Any) -> None:
        pass
