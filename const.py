from __future__ import annotations

import sublime
from lsp_utils import PlatformAssets

# @see https://github.com/latex-lsp/texlab/releases
SERVER_VERSION = "v5.26.0"

PLUGIN_NAME = "LSP-TexLab"
SETTINGS_FILENAME = f"{PLUGIN_NAME}.sublime-settings"

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
ST_CHANNEL = sublime.channel()
ST_VERSION = sublime.version()
