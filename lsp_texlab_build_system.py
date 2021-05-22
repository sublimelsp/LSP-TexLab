import sublime_plugin


class LspTexlabBuildSystemCommand(sublime_plugin.WindowCommand):
    def is_enabled(self, lint=False, integration=False, kill=False) -> bool:
        return True

    def run(self, lint=False, integration=False, kill=False):
        if kill:
            print("TexLab: Killing builds is not supported")
            return
        self.window.active_view().run_command("lsp_texlab_build")
        # Diabled: With TexLab 3+ user should use "-pvc"
        # self.window.active_view().run_command("lsp_texlab_forward_search")
