import inspect
import os
import fnmatch


def get_rattletrap_path():
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    return path


def get_rattletrap_binaries(path):
    files = os.listdir(path)
    binaries = [f for f in files if not f.endswith('.py') and fnmatch.fnmatch(f, "*rattletrap*")]
    print(binaries)
    return binaries


def download_rattletrap():
    from rattletrap.check_rattletrap_version import update_rattletrap
    update_rattletrap()
