import argparse
import json
import os
import shutil
from pathlib import Path

class AssassinsCreedShadowsCleaner:

    DEFAULT_SUFFIXES = {".mesh", ".texture", ".textureset", ".texturemap"}

    def __init__(self, root_dir, listing="white", suffixes=None,remove_single_textures=False):
        self.root_dir = Path(root_dir).expanduser()
        self.listing = listing
        self.suffixes = {suffix.lower() for suffix in (suffixes or self.DEFAULT_SUFFIXES)}
        self.remove_single_textures = remove_single_textures

    def main(self):
        if not self.root_dir.exists():
            print(f"Error: Directory does not exist: {self.root_dir}")
            return 0

        if not self.root_dir.is_dir():
            print(f"Error: Not a directory: {self.root_dir}")
            return 0

        deleted_count = self.scan_and_clean()
        print(f"Number of entries deleted in {self.root_dir}: {deleted_count}")
        return deleted_count

    def scan_and_clean(self):
        root_dir = self.root_dir.resolve()

        if not root_dir.is_dir():
            print(f"Error: Directory not found:")
            print(root_dir)
            return

        print(f"Scanning: {root_dir}")
        print("=" * 60)

        deleted_count = 0
        for current_root, directories, files in os.walk(root_dir, topdown=False):
            for filename in files:
                file_path = os.path.join(current_root, filename)
                extension = Path(filename).suffix.lower()
                listed = extension in self.suffixes
                should_delete = listed if self.listing == "black" else not listed

                if should_delete:
                    try:
                        os.remove(file_path)
                        print(f"[DELETED] {file_path}")
                        deleted_count += 1

                    except OSError as error:
                        print(f"[ERROR] {file_path}")
                        print(f"         {error}")

            if not Path(current_root).is_dir():
                continue

            try:
                remaining_items = os.listdir(current_root)

                if len(remaining_items) == 0:
                    if Path(current_root).resolve() != root_dir:
                        os.rmdir(current_root)
                        print(f"[DIRECTORY DELETED] {current_root}")
                        deleted_count += 1

            except Exception as e:
                print(f"[ERROR WHILE CHECKING] {current_root}")
                print(f"                    {e}")

            if not self.remove_single_textures or not Path(current_root).is_dir():
                continue

            remaining_items = os.listdir(current_root)
            if len(remaining_items) != 1:
                continue

            single_texture = Path(current_root) / remaining_items[0]
            if not single_texture.is_file() or single_texture.suffix.lower() != ".texturemap":
                continue

            try:
                os.remove(single_texture)
                print(f"[DELETED] {single_texture}")
                deleted_count += 1
                if single_texture.parent.resolve() != root_dir:
                    os.rmdir(single_texture.parent)
                    print(f"[DIRECTORY DELETED] {single_texture.parent}")
                    deleted_count += 1
            except OSError as error:
                print(f"[ERROR] {single_texture}")
                print(f"         {error}")
        return deleted_count

    @staticmethod
    def parse_suffix(value):
        suffix = value.strip().strip("{}[],'\"").lower()
        if not suffix.startswith(".") or len(suffix) == 1:
            raise argparse.ArgumentTypeError('expected a file suffix such as ".mesh"')
        return suffix


    @staticmethod
    def parse_suffix_list(value):
        value = value.strip()
        if value.startswith("["):
            try:
                suffixes = json.loads(value)
            except json.JSONDecodeError as error:
                suffixes = [item.strip() for item in value[1:-1].split(",") if item.strip()]
                if not suffixes:
                    raise argparse.ArgumentTypeError(f"expected a suffix list: {error.msg}")
            if not isinstance(suffixes, list) or not suffixes:
                raise argparse.ArgumentTypeError("expected a non-empty suffix list")
        else:
            suffixes = [value]

        try:
            return [AssassinsCreedShadowsCleaner.parse_suffix(suffix) for suffix in suffixes]
        except AttributeError:
            raise argparse.ArgumentTypeError("every suffix must be a string")


    @staticmethod
    def parse_boolean(value):
        normalized_value = value.strip().lower()
        if normalized_value == "true":
            return True
        if normalized_value == "false":
            return False
        raise argparse.ArgumentTypeError("expected True or False")


    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(description="Cleans files and empty directories.")
        parser.add_argument("--root_dir", required=True, metavar="DIRECTORY",
                        help="Starting directory to scan")
        parser.add_argument("--listing", choices=("white", "black"), default="white")
        parser.add_argument("--suffix", type=AssassinsCreedShadowsCleaner.parse_suffix_list, metavar="SUFFIXES",
                        help='Specify one suffix or a list, e.g. --suffix \'[".mesh", ".texturemap"]\'')
        parser.add_argument("--remove_single_textures", type=AssassinsCreedShadowsCleaner.parse_boolean, default=False,
                        metavar="True|False",
                        help="Delete folders containing only one .texturemap file")
        arguments = parser.parse_args()
        suffix_values = arguments.suffix or AssassinsCreedShadowsCleaner.DEFAULT_SUFFIXES
        arguments.suffix = {suffix.lower() for suffix in suffix_values}
        return arguments


if __name__ == "__main__":
    arguments = AssassinsCreedShadowsCleaner.parse_arguments()
    total_deleted = AssassinsCreedShadowsCleaner(
        arguments.root_dir,
        listing=arguments.listing,
        suffixes=arguments.suffix,
        remove_single_textures=arguments.remove_single_textures,
    ).main()

    print(f"Total number of entries deleted: {total_deleted}")