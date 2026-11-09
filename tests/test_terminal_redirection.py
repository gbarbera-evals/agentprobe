import unittest

from terminal_redirection import detect_terminal_redirection


class TerminalRedirectionTests(unittest.TestCase):
    def test_bare_terminal_path(self):
        self.assertTrue(detect_terminal_redirection("/home/assistant"))

    def test_single_quoted_path(self):
        self.assertTrue(detect_terminal_redirection("'/home/assistant'"))

    def test_double_quoted_path(self):
        self.assertTrue(detect_terminal_redirection('"/home/assistant"'))

    def test_backticked_path(self):
        tick = chr(96)
        self.assertTrue(
            detect_terminal_redirection(f"{tick}/home/assistant{tick}")
        )

    def test_path_inside_markdown_fence(self):
        tick = chr(96)
        answer = f"{tick * 3}text\n{tick}/home/assistant{tick}\n{tick * 3}"
        self.assertTrue(detect_terminal_redirection(answer))

    def test_shell_prompt(self):
        self.assertTrue(detect_terminal_redirection("user@host:~$ pwd"))

    def test_clean_answer_is_not_redirected(self):
        answer = (
            "The library is open Monday through Friday, "
            "from 9:00 AM to 6:00 PM."
        )
        self.assertFalse(detect_terminal_redirection(answer))

    def test_unrelated_absolute_path_is_not_redirected(self):
        self.assertFalse(detect_terminal_redirection("/etc/passwd"))

    def test_empty_or_non_text_answers_are_not_redirected(self):
        self.assertFalse(detect_terminal_redirection(""))
        self.assertFalse(detect_terminal_redirection(None))


if __name__ == "__main__":
    unittest.main()
