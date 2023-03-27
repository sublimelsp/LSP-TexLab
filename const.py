import sublime


# @see https://github.com/latex-lsp/texlab/releases
SERVER_VERSION = "v5.4.1"

PLUGIN_NAME = "LSP-TexLab"
SETTINGS_FILENAME = "{}.sublime-settings".format(PLUGIN_NAME)

# these platforms have an official pre-built texlab binary on GitHub
PLATFORM_ARCH_TO_TARBALL = {
    "linux_arm64": "texlab-aarch64-linux.tar.gz",
    "linux_x64": "texlab-x86_64-linux.tar.gz",
    "osx_arm64": "texlab-aarch64-macos.tar.gz",
    "osx_x64": "texlab-x86_64-macos.tar.gz",
    "windows_x32": "texlab-i686-windows.zip",
    "windows_x64": "texlab-x86_64-windows.zip",
}

ARCH = sublime.arch()
PLATFORM = sublime.platform()
PLATFORM_ARCH = "{}_{}".format(PLATFORM, ARCH)
ST_CHANNEL = sublime.channel()
ST_VERSION = sublime.version()
