import argparse
import os
from typing import Tuple


class File:
    def __init__(self, path: str, folder=False):
        self.path = path
        self.folder = folder
        self._converted_name = None

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    @property
    def dir_path(self) -> str:
        return os.path.dirname(self.path)

    @property
    def converted_name(self) -> str:
        return self._converted_name

    @converted_name.setter
    def converted_name(self, name: str) -> None:
        self._converted_name = name


def valid_path(path: str) -> str:
    if os.path.exists(path):
        return path
    raise argparse.ArgumentTypeError("{} is not a valid path".format(path))


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert a file or every file in directory name from one encoding to "
                                                 "other")
    parser.add_argument("path", type=valid_path, help="Valid file or directory path")
    parser.add_argument("-s", "--source", type=str, help="Source encoding of the file", metavar="source", required=True)
    parser.add_argument("-t", "--target", type=str, help="Target encoding of the file", metavar="target", required=True)
    parser.add_argument("-r", "--recursive", type=bool, help="Renames sub folders in directory in passed"
                        , action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("-i", "--ignore-errors", type=bool, help="Ignore encoding errors if present"
                        , action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("-d", "--directories", type=bool, help="Renames folders as well as files"
                        , action=argparse.BooleanOptionalAction, default=False)
    return parser


def get_file_paths(path: str, recursive=False) -> Tuple[list[str], list[str]]:
    list_of_files = []
    list_of_folders = []
    for base_path, dirs, files in os.walk(path):
        for file in files:
            list_of_files.append(os.path.join(base_path, file))
        for folder in dirs:
            list_of_folders.append(os.path.join(base_path, folder))
        if not recursive:
            break
    return list_of_files, list_of_folders


def create_file_tree(path: str, recursive=False) -> Tuple[list[File], list[File]]:
    all_files = []
    all_folders = []
    if os.path.isfile(path):
        all_files.append(File(path))
    else:
        file_paths, folder_paths = get_file_paths(path, recursive)
        all_files = map(lambda x: File(x), file_paths)
        all_folders = map(lambda x: File(x, True), folder_paths)
    return all_files, all_folders


def convert_file_name(file_name, source, target):
    str_enc = file_name.encode(source)
    return str_enc.decode(target)


def rename_file(file: File) -> None:
    if file.converted_name is not None:
        old_name = file.path
        new_name = os.path.join(file.dir_path, file.converted_name)
        os.rename(old_name, new_name)
        print("{} file is renamed to: {}".format(old_name, new_name), end="\n")
    pass


def rename_file_list(file_list: list[File], source: str, target: str, ignore_errors=False) -> None:
    for file in file_list:
        file_name = file.name
        try:
            converted_name = convert_file_name(file_name, source, target)
            file.converted_name = converted_name
            rename_file(file)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            if ignore_errors:
                print("{} file cannot be processed".format(file_name), end="\n")
            else:
                raise e
    pass


def run():
    arg_parser = create_parser()
    result = vars(arg_parser.parse_args())
    file_list, folder_list = create_file_tree(result["path"], result["recursive"])
    rename_file_list(file_list, result["source"], result["target"], result["ignore_errors"])
    if result["directories"]:
        rename_file_list(folder_list, result["source"], result["target"], result["ignore_errors"])


if __name__ == '__main__':
    run()
