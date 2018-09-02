import os
import shutil
from tempfile import mkstemp

from .create_proto import get_file_list

import_statement = 'import '


def analyze_file(deepness, file_path, top_level_import):
    replace_map = dict()
    fh, abs_path = mkstemp()
    modified = False
    with os.fdopen(fh, 'w') as new_file:
        with open(file_path, 'r') as old_file:
            lines = old_file.readlines()
            for i in range(len(lines)):
                line = lines[i]
                extra_cases = '.' in line and top_level_import in line and not (import_statement + '.') in line
                if line.startswith(import_statement) and extra_cases:
                    cut_line = line[len(import_statement):].rstrip()
                    ending_string = cut_line[cut_line.rfind('.') + 1:]
                    replace_map[cut_line] = ending_string
                    line = 'from ' + '.' * deepness + cut_line[:cut_line.rfind(ending_string) - 1] + ' import ' + ending_string + '\n'
                    modified = True
                else:
                    for key in replace_map:
                        if key in line:
                            modified = True
                            line = line.replace(key, replace_map[key])
                new_file.write(line)
    if modified:
        os.remove(file_path)
        shutil.move(abs_path, file_path)
        print(str(len(replace_map)), 'imports')
    else:
        print('not modified')


def convert_to_relative_imports(top_level_dir='generated', exclude_dir=None, top_level_import="api"):
    print('###FIXING IMPORTS###')
    file_list = get_file_list(top_level_dir, exclude_dir)
    for file in file_list:
        print('fixing file: ', file[1], end='\t')
        analyze_file(file[0], file[1], top_level_import)


# prevent_leaks("replay_analysis", "generated", "replay_analysis")
if __name__ == '__main__':
    convert_to_relative_imports()

"""
Hi All  This file converts protobuf imports to relative imports so instead of
import api.player_pb2
it does
import ...api.player_pb2

The reason for this is described here:
https://github.com/protocolbuffers/protobuf/issues/1491

Basically google does not allow relative imports from their generated protobuf code.
So we do it so that our genreated file can go in a folder we dont care about

"""
