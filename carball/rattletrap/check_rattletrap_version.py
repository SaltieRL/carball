import json
import os
import logging
from distutils.version import StrictVersion
from shutil import copyfile
from urllib import request

from carball.rattletrap.rattletrap_utils import get_rattletrap_path, get_binary_version, \
    get_all_binaries, get_highest_binary, get_rattletrap_binaries

log = logging.getLogger(__name__)


def update_rattletrap():
    path = get_rattletrap_path()

    cur_ver = StrictVersion('0.0.0')
    binaries = get_all_binaries(path)

    try:
        response = request.urlopen('https://api.github.com/repos/tfausak/rattletrap/releases/latest')
        js = json.loads(response.read())
        github_ver = StrictVersion(js['name'])
    except:
        log.warning('Unable to download rattletrap copying backup')
        # unable to download a new rattletrap version so we should just copy our own
        github_ver = StrictVersion(cur_ver)
        copyfile(os.path.join(get_rattletrap_path(),
                              list(filter(lambda file_name: 'cloud_parser' in str(file_name), binaries))[0]),
                 os.path.join(get_rattletrap_path(), 'rattletrap-linux'))
        os.chmod(os.path.join(get_rattletrap_path(), 'rattletrap-linux'), 0o777)
        return

    if len(binaries) > 0:
        cur_ver = get_binary_version(get_highest_binary(binaries)[0])
    update = github_ver > cur_ver
    log.info(f'GitHub version: {js["name"]}\n'
             f'Current version: {cur_ver}\n'
             f'Update? {update}')
    if update:
        for file in get_rattletrap_binaries(path):
            os.remove(os.path.join(path, file))

        for asset in js['assets']:
            log.info('Downloading {}'.format(asset['name']))
            new_file = os.path.join(path, asset['name'])
            request.urlretrieve(asset['browser_download_url'], filename=new_file)
            log.info('making file executable', new_file)
            os.chmod(new_file, 0o777)


if __name__ == "__main__":
    update_rattletrap()
