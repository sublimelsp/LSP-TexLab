import sublime


# @see https://github.com/latex-lsp/texlab/releases
SERVER_VERSION = "v2.2.2"

PLUGIN_NAME = "LSP-TexLab"
SETTINGS_FILENAME = "{}.sublime-settings".format(PLUGIN_NAME)

ARCH = sublime.arch()
PLATFORM = sublime.platform()
ST_CHANNEL = sublime.channel()
ST_VERSION = sublime.version()
