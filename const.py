import sublime


# @see https://github.com/latex-lsp/texlab/releases
SERVER_VERSION = "v3.2.0"

PLUGIN_NAME = "LSP-TexLab"
SETTINGS_FILENAME = "{}.sublime-settings".format(PLUGIN_NAME)

ARCH = sublime.arch()
PLATFORM = sublime.platform()
PLATFORM_ARCH = "{}_{}".format(PLATFORM, ARCH)
ST_CHANNEL = sublime.channel()
ST_VERSION = sublime.version()
