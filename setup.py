import json
import os

import setuptools
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

with open(os.path.join('carball', 'analysis', 'PROTOBUF_VERSION'), 'r') as f:
    PROTOBUF_VERSION = json.loads(f.read())


with open(os.path.join('CARBALL_VERSION'), 'r') as f:
    subversion = json.loads(f.read())

version_string = '0.' + str(PROTOBUF_VERSION) + '.' + str(subversion)

if os.path.isfile('README.md'):
    with open("README.md", "r") as readme_file:
        long_description = readme_file.read()
else:
    long_description = ''


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        from init import initialize_project
        initialize_project()
        # this needs to be last
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        from init import initialize_project
        initialize_project()
        # this needs to be last
        install.run(self)


setup(
    name='carball',
    version=version_string,
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=['pandas==0.24.2', 'protobuf==3.6.1', 'xlrd==1.1.0', 'numpy==1.17.0'],
    url='https://github.com/SaltieRL/carball',
    keywords=['rocket-league'],
    license='Apache 2.0',
    author='Matthew Mage, Harry Xie, David Turner',
    author_email='sciguymjm@gmail.com',
    description='Rocket League replay parsing and analysis.',
    long_description=long_description,
    exclude_package_data={'': ['.gitignore', '.git/*', '.git/**/*', 'replays/*']},
    long_description_content_type='text/markdown',
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    entry_points={
        'console_scripts': ['carball=carball.command_line:main']
    }
)
