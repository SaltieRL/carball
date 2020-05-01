def initialize_project():
    print("Importing necessary methods...")
    from utils.create_proto import create_proto_files
    from utils.import_fixer import convert_to_relative_imports

    print("Creating proto files...")
    create_proto_files()
    convert_to_relative_imports()


if __name__ == "__main__":
    print("Initialising project...")
    initialize_project()
