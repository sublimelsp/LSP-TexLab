from __future__ import annotations

from typing import Any, TypedDict

import sublime
from LSP.plugin import (
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
from typing_extensions import NotRequired

from .const import PLUGIN_NAME
from .server import install_server


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
            server_bin = install_server(cls.plugin_storage_path)
        # for unofficially supported platforms, users have to compile texlab by themselves
        # and adjust the "command" to use the executable (or have it on the PATH)
        context.variables["texlab_bin"] = str(server_bin) if server_bin else "texlab"


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
