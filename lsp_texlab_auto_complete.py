import sublime
import sublime_plugin


class LspTexlabAutoCompleteCommand(sublime_plugin.TextCommand):
    """
    This command is used to override ST's built-in `{` keybindings.

    Originally, if the user press `{`, it will trigger ST's built-in command to insert `{$0}` snippet.
    But then, the AC will not be triggered after that. The user would have to trigger AC manually.
    Thus, we use this command, which will trigger AC, to override ST's built-in.
    """

    def run(self, edit: sublime.Edit) -> None:
        self.view.run_command("insert_snippet", {"contents": "{$0}"})
        # Do auto-complete one tick later, otherwise LSP is not up-to-date with
        # the incremental text sync.
        sublime.set_timeout(lambda: self.view.run_command("auto_complete"))
