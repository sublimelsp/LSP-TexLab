from .const import ARCH
from .const import MANAGED_PLATFORM_ARCHS
from .const import PLATFORM
from .const import PLATFORM_ARCH
from .const import PLUGIN_NAME
from .const import SERVER_VERSION
from .server import get_default_server_bin_path
from .server import get_plugin_storage_dir
from .server import get_server_dir
from .server import get_server_download_url
from .tarball import decompress
from .tarball import download
from LSP.plugin import AbstractPlugin
from LSP.plugin import Request
from LSP.plugin.core.registry import LspTextCommand
from LSP.plugin.core.typing import Any, Dict, List, Tuple
from LSP.plugin.core.views import extract_variables
from LSP.plugin.core.views import text_document_identifier
from LSP.plugin.core.views import text_document_position_params
import os
import shutil
import sublime


class LspTexLabPlugin(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return PLUGIN_NAME

    @classmethod
    def configuration(cls) -> Tuple[sublime.Settings, str]:
        name = cls.name()
        basename = "{}.sublime-settings".format(name)
        filepath = "Packages/{}/{}".format(name, basename)
        return sublime.load_settings(basename), filepath

    @classmethod
    def additional_variables(cls) -> Dict[str, str]:
        return {
            "texlab_bin": get_default_server_bin_path() if PLATFORM_ARCH in MANAGED_PLATFORM_ARCHS else "texlab",
        }

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        command = cls.configuration()[0].get("command")  # type: List[str]
        server_bin = command[0]

        # only auto manage platforms which the official server supports
        if PLATFORM_ARCH in MANAGED_PLATFORM_ARCHS and server_bin in {"${texlab_bin}", "$texlab_bin"}:
            variables = extract_variables(sublime.active_window())
            variables.update(cls.additional_variables())
            server_bin = sublime.expand_variables(server_bin, variables)
            return not os.path.isfile(server_bin)

        # for unofficial supported platforms, users have to compile texlab by themselves
        # and adjust the "command" to use the executable
        return False

    @classmethod
    def install_or_update(cls) -> None:
        cls._cleanup_cache()

        is_download_ok = cls._prepare_server_bin()
        if not is_download_ok:
            raise RuntimeError("Unable to download the server binary...")

    @classmethod
    def _prepare_server_bin(cls) -> bool:
        """Download the LSP server binary."""

        server_dir = get_server_dir()
        download_url = get_server_download_url(SERVER_VERSION, PLATFORM, ARCH)
        if not download_url:
            return False

        tarball_name = download_url.split("/")[-1]
        tarball_path = os.path.join(server_dir, tarball_name)

        download(download_url, tarball_path)
        decompress(tarball_path, server_dir)

        return True

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
