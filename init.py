def initialize_project():
    from rattletrap.check_rattletrap_version import update_rattletrap
    from utils.create_proto import create_proto_files
    from utils.import_fixer import convert_to_relative_imports

    create_proto_files()
    convert_to_relative_imports()
    update_rattletrap()


if __name__ == "__main__":
    initialize_project()
