from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict

import sublime
from LSP.plugin import (
    ClientConfig,
    LspPlugin,
    LspTextCommand,
    OnPreStartContext,
    Request,
    first_selection_region,
    offset_to_position,
    text_document_identifier,
    text_document_position_params,
)
from LSP.protocol import Position, TextDocumentIdentifier
from lsp_utils import (
    InstallDirectory,
    PlatformAssets,
    UnsupportedPlatformError,
    download_and_extract,
    select_platform_asset,
)
from typing_extensions import NotRequired

# @see https://github.com/latex-lsp/texlab/releases
SERVER_VERSION = "v5.26.0"

PLUGIN_NAME = "LSP-TexLab"

# these platforms have an official pre-built texlab binary on GitHub
SERVER_ASSETS: PlatformAssets = {
    "linux-arm64": "texlab-aarch64-linux.tar.gz",
    "linux-x64": "texlab-x86_64-linux.tar.gz",
    "osx-arm64": "texlab-aarch64-macos.tar.gz",
    "osx-x64": "texlab-x86_64-macos.tar.gz",
    "windows-arm64": "texlab-aarch64-windows.zip",
    "windows-x32": "texlab-i686-windows.zip",
    "windows-x64": "texlab-x86_64-windows.zip",
}

PLATFORM = sublime.platform()
SERVER_BINARY = "texlab.exe" if PLATFORM == "windows" else "texlab"


class TextDocumentBuildParams(TypedDict):
    textDocument: TextDocumentIdentifier
    position: NotRequired[Position]


def plugin_loaded() -> None:
    LspTexLabPlugin.register()


def plugin_unloaded() -> None:
    LspTexLabPlugin.unregister()


class LspTexLabPlugin(LspPlugin):
    @classmethod
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        server_bin = None
        # only auto manage the server when the "command" uses it, on platforms which the official server supports
        if context.configuration.command[:1] in (["${texlab_bin}"], ["$texlab_bin"]):
            server_bin = cls._install_server(context.configuration)
        # for unofficially supported platforms, users have to compile texlab by themselves
        # and adjust the "command" to use the executable (or have it on the PATH)
        context.variables["texlab_bin"] = str(server_bin) if server_bin else "texlab"

    @classmethod
    def _install_server(cls, configuration: ClientConfig) -> Path | None:
        """
        Installs the LSP server, unless already installed, and gets the path of its binary.

        :returns:   The path of the server binary or `None` if there is no pre-built server for the current platform.
        """

        try:
            asset = select_platform_asset(SERVER_ASSETS)
        except UnsupportedPlatformError:
            return None
        url = cls._get_server_download_url(configuration, asset)
        if not url:
            return None

        storage_dir = cls.plugin_storage_path
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

    @staticmethod
    def _get_server_download_url(configuration: ClientConfig, asset: str) -> str | None:
        """
        Gets the LSP server download URL.

        :param      asset:  The file name of the release asset
        """

        url = configuration.root_settings.get("lsp_server_download_url")
        if not isinstance(url, str) or not url:
            return None

        return url.format_map(
            {
                "version": SERVER_VERSION,
                "version_without_v": SERVER_VERSION.lstrip("v"),
                "tarball": asset,
            }
        )


class LspTexlabForwardSearchCommand(LspTextCommand):
    session_name = PLUGIN_NAME

    def run(self, _: sublime.Edit) -> None:
        session = self.session_by_name(PLUGIN_NAME)
        if not session:
            return
        params = text_document_position_params(self.view, next(iter(self.view.sel())).a)
        session.send_request(
            Request("textDocument/forwardSearch", params),
            self.on_response_async,
            self.on_error_async,
        )

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
            window.status_message(
                PLUGIN_NAME + ": Previewer failed to start or crashed"
            )
        elif status == 3:
            window.status_message(PLUGIN_NAME + ": Previewer is not configured")

    def on_error_async(self, error: Any) -> None:
        pass


class LspTexlabBuildCommand(LspTextCommand):
    session_name = PLUGIN_NAME

    def run(self, _: sublime.Edit) -> None:
        session = self.session_by_name(PLUGIN_NAME)
        if not session:
            return
        params: TextDocumentBuildParams = {"textDocument": text_document_identifier(self.view)}
        region = first_selection_region(self.view)
        if region is not None:
            params["position"] = offset_to_position(self.view, region.b)

        session.send_request(
            Request("textDocument/build", params),
            self.on_response_async,
            self.on_error_async,
        )

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
