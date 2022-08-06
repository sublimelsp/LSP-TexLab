import sublime


# @see https://github.com/latex-lsp/texlab/releases
SERVER_VERSION = "v4.2.1"

PLUGIN_NAME = "LSP-TexLab"
SETTINGS_FILENAME = "{}.sublime-settings".format(PLUGIN_NAME)

# these platforms have an official pre-built texlab binary on GitHub
MANAGED_PLATFORM_ARCHS = {
    "linux_arm64",
    "linux_x64",
    "osx_arm64",
    "osx_x64",
    "windows_x32",
    "windows_x64",
}

ARCH = sublime.arch()
PLATFORM = sublime.platform()
PLATFORM_ARCH = "{}_{}".format(PLATFORM, ARCH)
ST_CHANNEL = sublime.channel()
ST_VERSION = sublime.version()
