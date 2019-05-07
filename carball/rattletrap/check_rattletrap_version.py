import json
import os
from distutils.version import StrictVersion
from shutil import copyfile
from urllib import request

from carball.rattletrap.rattletrap_utils import get_rattletrap_binaries, get_rattletrap_path


def update_rattletrap():
    path = get_rattletrap_path()

    cur_ver = '0.0.0'
    binaries = get_rattletrap_binaries(path)

    try:
        response = request.urlopen('https://api.github.com/repos/tfausak/rattletrap/releases/latest')
        js = json.loads(response.read())
        github_ver = StrictVersion(js['name'])
    except:
        print('Unable to download rattletrap copying backup')
        # unable to download a new rattletrap version so we should just copy our own
        github_ver = StrictVersion(cur_ver)
        copyfile(os.path.join(get_rattletrap_path(), 'cloud_parser'),
                 os.path.join(get_rattletrap_path(), 'rattletrap-linux'))
        os.chmod(os.path.join(get_rattletrap_path(), 'rattletrap-linux'), 0o777)
        return

    if len(binaries) > 0:
        cur_ver = binaries[0].split('-')[1]
    update = github_ver > StrictVersion(cur_ver)
    print(f'GitHub version: {js["name"]}\n'
          f'Current version: {cur_ver}\n'
          f'Update? {update}')
    if update:
        for file in binaries:
            os.remove(file)

        for asset in js['assets']:
            print('Downloading {}'.format(asset['name']))
            new_file = os.path.join(path, asset['name'])
            request.urlretrieve(asset['browser_download_url'], filename=new_file)
            print('making file executable', new_file)
            os.chmod(new_file, 0o777)


if __name__ == "__main__":
    update_rattletrap()
