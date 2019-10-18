import os
from unittest.mock import patch

from requests import HTTPError

from carball.rattletrap.rattletrap_utils import get_rattletrap_binaries, get_rattletrap_path, download_rattletrap
from carball.rattletrap.run_rattletrap import create_rattletrap_command
from carball.rattletrap.check_rattletrap_version import update_rattletrap


class Test_rattletrapSetup():

    def cleanup(self):
        path = get_rattletrap_path()
        binaries = get_rattletrap_binaries(get_rattletrap_path())

        # clean out existing
        for binary in binaries:
            os.remove(os.path.join(path, binary))

    def test_rattle(self):
        self.cleanup()

        download_rattletrap()

    def test_create_rattletrap_command(self):
        self.cleanup()

        create_rattletrap_command('file.replay', 'outputdir')

        # check post download
        create_rattletrap_command('file.replay', 'outputdir2')

    def test_direct_check_version(self):
        self.cleanup()
        update_rattletrap()

        #skip update
        update_rattletrap()

    def test_get_correct_version_from_platform(self):
        path = get_rattletrap_path()
        binaries = get_rattletrap_binaries(get_rattletrap_path())

    @patch("urllib.request.urlopen")
    def test_403_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError()

        update_rattletrap()

        self.cleanup()
