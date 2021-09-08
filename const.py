import sublime


# @see https://github.com/latex-lsp/texlab/releases
SERVER_VERSION = "v3.2.0"

PLUGIN_NAME = "LSP-TexLab"
SETTINGS_FILENAME = "{}.sublime-settings".format(PLUGIN_NAME)
MANAGED_PLATFORM_ARCHS = ("windows_x64", "linux_x64", "osx_x64")

ARCH = sublime.arch()
PLATFORM = sublime.platform()
PLATFORM_ARCH = "{}_{}".format(PLATFORM, ARCH)
ST_CHANNEL = sublime.channel()
ST_VERSION = sublime.version()
