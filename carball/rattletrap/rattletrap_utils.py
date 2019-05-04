import inspect
import os
import fnmatch
from typing import List, Union


def get_rattletrap_path() -> Union[bytes, str]:
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    return path


def get_rattletrap_binaries(path: Union[bytes, str]) -> List[Union[bytes, str]]:
    files = os.listdir(path)
    binaries = [f for f in files if not f.endswith('.py') and fnmatch.fnmatch(f, "*rattletrap*")]
    print(binaries)
    return binaries


def download_rattletrap():
    from carball.rattletrap.check_rattletrap_version import update_rattletrap
    update_rattletrap()
