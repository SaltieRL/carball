import os
import platform
from subprocess import call


def is_windows():
    return platform.system() == 'Windows'


current_dir = os.path.dirname(os.path.dirname(__file__))


proto_dir = os.path.join(current_dir, 'carball', 'generated')


def get_proto():
    if is_windows():
        return os.path.join(proto_dir, 'protoc.exe')
    else:
        return os.path.join(proto_dir, 'protoc')


def split_to_list(drive_and_path):
    path = os.path.splitdrive(drive_and_path)[1]
    folders = []
    while 1:
        path, folder = os.path.split(path)

        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)

            break

    folders.reverse()
    return folders


def get_deepness(top_level_dir, path_list):
    return len(path_list) - path_list.index(top_level_dir)


def get_file_list(top_level_dir, exclude_dir=None, file_extension='.py'):
    proto_dir = [x[0] for x in os.walk(current_dir) if top_level_dir in x[0] and '__pycache__' not in x[0]]

    file_result = []

    path_lists = []
    for path in proto_dir:
        if exclude_dir is not None and exclude_dir in path:
            continue
        path_list = split_to_list(path)
        deepness = get_deepness(top_level_dir, path_list)
        left_over_paths = path_list[-deepness:]
        path_lists.append((path, deepness, left_over_paths))
    for path_item in path_lists:
        path = path_item[0]
        only_files = [(os.path.join(path, f), f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
                      and file_extension in f and '__init__' not in f]
        for file in only_files:
            file_result.append((path_item[1], file[0]))
    return file_result


def create_proto_files():
    print('###CREATING PROTO FILES###')
    file_list = get_file_list(top_level_dir='api', file_extension='.proto')
    for file in file_list:
        path = file[0]
        file = file[1]
        print('creating proto file', file, end='\t')
        result = call([get_proto(), '--python_out=' + proto_dir, '--proto_path=' + current_dir, file])
        print(result)


if __name__ == "__main__":
    create_proto_files()
