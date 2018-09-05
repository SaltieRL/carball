import os
from urllib import request
import json
from distutils.version import StrictVersion

response = request.urlopen('https://api.github.com/repos/tfausak/rattletrap/releases/latest')

js = json.loads(response.read())

cur_ver = '0.0.0'
binaries = [f for f in os.listdir('.') if not f.endswith('.py')]
print (binaries)
if len(binaries) > 0:
    cur_ver = binaries[0].split('-')[1]
update = StrictVersion(js['name']) > StrictVersion(cur_ver)
print (f'GitHub version: {js["name"]}\n'
       f'Current version: {cur_ver}\n'
       f'Update? {update}')
if update:
    for file in binaries:
        os.remove(file)

    for asset in js['assets']:

        print('Downloading {}'.format(asset['name']))
        request.urlretrieve(asset['browser_download_url'], asset['name'])