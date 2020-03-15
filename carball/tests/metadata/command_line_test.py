import pytest

from carball.command_line import main
from carball.tests.utils import get_replay_path, get_raw_replays


class Test_Commandline():
    def test_command_line_valid_input(self):
        replay_path = get_replay_path(get_raw_replays()["KICKOFF_NO_TOUCH"][0])
        main(program_args=["--i", replay_path, "-v", "--dry-run"])

    def test_command_line_invalid_input(self):
        replay_path = get_replay_path("INVALID_REPLAY")
        with pytest.raises(FileNotFoundError):
            main(program_args=["--i", replay_path, "-s", "--proto", "PATH_DOESNT_MATTER"])

    def test_command_line_no_output(self):
        replay_path = get_replay_path(get_raw_replays()["KICKOFF_NO_TOUCH"][0])
        with pytest.raises(SystemExit):
            main(program_args=["--i", replay_path])
