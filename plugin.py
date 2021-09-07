from .const import ARCH
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
            "texlab_bin": "texlab" if PLATFORM_ARCH == "osx_arm64" else get_default_server_bin_path(),
        }

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        command: List[str] = cls.configuration()[0].get("command")
        server_bin = command[0]

        if (
            # auto install/update unsupported
            PLATFORM_ARCH == "osx_arm64"
            # the user want to manager it by himself
            or server_bin not in ("${texlab_bin}", "$texlab_bin")
        ):
            return False

        variables = extract_variables(sublime.active_window())
        variables.update(cls.additional_variables())
        server_bin = sublime.expand_variables(server_bin, variables)
        return not shutil.which(server_bin)

    @classmethod
    def install_or_update(cls) -> None:
        cls._cleanup_cache()

        is_download_ok = cls._prepare_server_bin()
        if not is_download_ok:
            raise RuntimeError(
                "Unable to download the server binary."
                + " If you are using Apple M1, you have to build 'texlab' via Homebrew Formulae"
                + " (see https://formulae.brew.sh/formula/texlab) by yourself."
            )

    @classmethod
    def _prepare_server_bin(cls) -> bool:
        """Download the LSP server binary."""

        server_dir = get_server_dir()
        download_url = get_server_download_url(SERVER_VERSION, ARCH, PLATFORM)
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
