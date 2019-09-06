import inspect
import os
import fnmatch
import logging
from typing import List, Union

log = logging.getLogger(__name__)


def get_rattletrap_path() -> Union[bytes, str]:
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    return path


def get_rattletrap_binaries(path: Union[bytes, str]) -> List[Union[bytes, str]]:
    files = os.listdir(path)
    binaries = [f for f in files if not f.endswith('.py') and fnmatch.fnmatch(f, "*rattletrap*")]
    log.debug(f'Discovered rattletrap binaries: {binaries}')
    return binaries


def download_rattletrap():
    from carball.rattletrap.check_rattletrap_version import update_rattletrap
    update_rattletrap()


def get_binary_for_platform(platform, binaries):
    if platform == 'Windows':
        binary = [f for f in binaries if f.endswith('.exe')][0]
    elif platform == 'Linux':
        binary = [f for f in binaries if 'linux' in f][0]
    elif platform == 'Darwin':
        binary = [f for f in binaries if 'osx' in f][0]
    else:
        raise Exception('Unknown platform, unable to process replay file.')
    return binary
