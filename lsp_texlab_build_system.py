import sublime_plugin


class LspTexlabBuildSystemCommand(sublime_plugin.WindowCommand):
    def is_enabled(self, lint: bool = False, integration: bool = False, kill: bool = False) -> bool:
        return True

    def run(self, lint: bool = False, integration: bool = False, kill: bool = False) -> None:
        if kill:
            print("TexLab: Killing builds is not supported")
            return

        view = self.window.active_view()
        if view:
            view.run_command("lsp_texlab_build")
        # Diabled: With TexLab 3+ user should use "-pvc"
        # self.window.active_view().run_command("lsp_texlab_forward_search")
