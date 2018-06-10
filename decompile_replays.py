import os
import subprocess


def decompile_replay(path):
    binaries = [f for f in os.listdir('rattletrap') if not f.endswith('.py')]
    if os.name == 'nt':
        binary = [f for f in binaries if f.endswith('.exe')][0]
        os.chdir(os.path.dirname(__file__))
        cmd = [f'rattletrap/{binary}', '-i', f'replays/{path}', '--output',
               f'replays/decompiled/{path.replace("replay", "json")}']
        print(cmd)
        subprocess.check_output(cmd)


if __name__ == '__main__':
    for p in [f for f in os.listdir('replays/') if os.path.isfile('replays/' + f)]:
        print(p)
        decompile_replay(p)
