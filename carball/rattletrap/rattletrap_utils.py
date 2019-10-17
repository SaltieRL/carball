import inspect
import os
import fnmatch
import logging
from distutils.version import StrictVersion
from shutil import copyfile
from typing import List, Union

log = logging.getLogger(__name__)


def get_rattletrap_path() -> Union[bytes, str]:
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    return path


def get_rattletrap_binaries(path: Union[bytes, str]) -> List[Union[bytes, str]]:
    files = os.listdir(path)
    binaries = [f for f in files if not f.endswith('.py') and (fnmatch.fnmatch(f, "*rattletrap*"))]
    log.debug(f'Discovered rattletrap binaries: {binaries}')
    return binaries


def get_all_binaries(path: Union[bytes, str]) -> List[Union[bytes, str]]:
    files = os.listdir(path)
    binaries = [f for f in files if not f.endswith('.py') and (fnmatch.fnmatch(f, "*rattletrap*") or
                                                               fnmatch.fnmatch(f, "*cloud_parser*"))]
    log.debug(f'Discovered rattletrap binaries: {binaries}')
    return binaries


def download_rattletrap():
    from carball.rattletrap.check_rattletrap_version import update_rattletrap
    update_rattletrap()


def get_binary_version(filename: str) -> StrictVersion:
    try:
        return StrictVersion(filename.split('-')[1])
    except:
        return StrictVersion('0.0.0')


def get_highest_binary(binaries):
    if len(binaries) == 1:
        return binaries[0]
    binaries.sort(key=lambda value: get_binary_version(str(value)))
    binary = binaries[-1]
    log.debug(binary)
    return binary


def get_binary_for_platform(platform, binaries):
    if platform == 'Windows':
        binaries = [f for f in binaries if f.endswith('.exe')]
    elif platform == 'Linux':
        binaries = [f for f in binaries if 'linux' in f]
    elif platform == 'Darwin':
        binaries = [f for f in binaries if 'osx' in f]
    else:
        raise Exception('Unknown platform, unable to process replay file.')

    return get_highest_binary(binaries)


def copy_cloud_over_to_rattletrap(binaries):
    cloud_binary = list(filter(lambda file_name: 'cloud_parser' in str(file_name), binaries))[0]
    version_info = get_binary_version(cloud_binary)
    linux_name = 'rattletrap-' + str(version_info) + '-linux'
    copyfile(os.path.join(get_rattletrap_path(), cloud_binary),
             os.path.join(get_rattletrap_path(), linux_name))
    os.chmod(os.path.join(get_rattletrap_path(), linux_name), 0o777)
    log.info("copied " + cloud_binary + " to " + linux_name)
