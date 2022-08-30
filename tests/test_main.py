import unittest

from click.testing import CliRunner

from vlcsync.cli_utils import parse_url
from vlcsync.cli import main
from vlcsync.vlc_state import VlcId


class SimpleTest(unittest.TestCase):
    @staticmethod
    def test_parse_url():
        expected = {VlcId("127.0.0.1", 21309)}
        actual = parse_url(None, None, {"127.0.0.1:21309"})
        assert expected == actual

    @staticmethod
    def test_invoke_help():
        runner = CliRunner(echo_stdin=True)
        runner.invoke(main, ["--help"])

    def test_invoke_wrong_host(self):
        runner = CliRunner(echo_stdin=True)
        result = runner.invoke(main, ["--rc-host", "sad:2134234"])

        assert result.exception
        print(result.stdout)
        self.assertIn("Error: Invalid value for '--rc-host'", result.stdout)
