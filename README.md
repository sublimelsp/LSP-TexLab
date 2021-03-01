# LSP-TexLab

LaTeX support for Sublime's LSP plugin provided through [latex-lsp/texlab](https://github.com/latex-lsp/texlab).

Note that this plugin requires ST >= 4070 and only supports x64 system.

## Installation

1. Install [LSP](https://packagecontrol.io/packages/LSP) and
   [LSP-TexLab](https://packagecontrol.io/packages/LSP-TexLab) via Package Control.
1. (Optional) Install [ChkTex](https://ctan.org/tex-archive/support/chktex) for linting.
1. Restart Sublime.

## Configuration

There are some ways to configure the package and the language server.

- From `Preferences > Package Settings > LSP > Servers > LSP-TexLab`
- From the command palette `Preferences: LSP-TexLab Settings`

## Sublime Commands

|Sublime Command           | Description                                                  |
|--------------------------|--------------------------------------------------------------|
|lsp_texlab_forward_search | Performs a forward search from the first cursor position     |
|lsp_texlab_build          | Build the current file                                       |

## For Plugin Developer

The targeted version of `texlab` is defined in `const.py`.

```py
# @see https://github.com/latex-lsp/texlab/releases
TEXLAB_VERSION = "v2.2.0"
```

If that version is not found on the machine, this plugin will try to download it.
