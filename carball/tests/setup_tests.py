import os
import unittest

from carball.rattletrap.rattletrap_utils import get_rattletrap_binaries, get_rattletrap_path, download_rattletrap


class setup_tests(unittest.TestCase):
    def test_rattle(self):
        binaries = get_rattletrap_binaries(get_rattletrap_path())

        # clean out existing
        for binary in binaries:
            os.remove(binary)

        download_rattletrap()
