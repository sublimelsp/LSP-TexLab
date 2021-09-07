import sublime
import sublime_plugin


class LspTexlabAutoCompleteCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        self.view.run_command("insert_snippet", {"contents": "{$0}"})
        # Do auto-complete one tick later, otherwise LSP is not up-to-date with
        # the incremental text sync.
        sublime.set_timeout(lambda: self.view.run_command("auto_complete"))
