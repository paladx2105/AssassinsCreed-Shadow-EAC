import argparse
import json
import os
import shutil
from pathlib import Path

class AssassinsCreedShadowsCleaner:

    DEFAULT_SUFFIXES = {".mesh", ".texture", ".textureset", ".texturemap"}

    def __init__(self, root_dir, listing="white", suffixes=None, remove_single_textures=False, remove_dir_without_mesh=False, remove_env_assets=False, file_size=10):
        self.root_dir = Path(root_dir).expanduser()
        self.listing = listing
        self.suffixes = {suffix.lower() for suffix in (suffixes or self.DEFAULT_SUFFIXES)}
        self.remove_single_textures = remove_single_textures
        self.remove_dir_without_mesh = remove_dir_without_mesh
        self.remove_env_assets = remove_env_assets
        self.file_size = file_size * 1024

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
            print(f"Error: Directory not found: {root_dir}")
            return 0

        print(f"Scanning: {root_dir}")
        print("=" * 60)

        deleted_count = 0
        for current_root, directories, files in os.walk(root_dir, topdown=False):
            current_path = Path(current_root)

            # 1. Option: Ordner ohne .mesh-Dateien komplett löschen
            if self.remove_dir_without_mesh and current_path != root_dir:
                has_mesh = False
                for sub_root, _, sub_files in os.walk(current_path):
                    if any(f.lower().endswith('.mesh') for f in sub_files):
                        has_mesh = True
                        break
                
                if not has_mesh:
                    try:
                        shutil.rmtree(current_path)
                        print(f"[NO MESH DIR DELETED] {current_path}")
                        deleted_count += 1
                        continue
                    except OSError as error:
                        print(f"[ERROR DELETING NO-MESH DIR] {current_path}: {error}")

            # 2. Option: Ordner mit .mesh-Dateien unter 10KB löschen (Environment Assets)
            if self.remove_env_assets and current_path != root_dir and current_path.is_dir():
                has_small_mesh = False
                for filename in files:
                    if filename.lower().endswith('.mesh'):
                        file_path = current_path / filename
                        try:
                            if file_path.stat().st_size < self.file_size:  # 10 KB = 10 * 1024 Bytes
                                has_small_mesh = True
                                break
                        except OSError as error:
                            print(f"[ERROR CHECKING FILE SIZE] {file_path}: {error}")
                
                if has_small_mesh:
                    try:
                        shutil.rmtree(current_path)
                        print(f"[ENV ASSET DIR DELETED] {current_path}")
                        deleted_count += 1
                        continue
                    except OSError as error:
                        print(f"[ERROR DELETING ENV ASSET DIR] {current_path}: {error}")

            # 3. Option: Ordner mit NUR einer einzelnen .texturemap-Datei löschen
            if self.remove_single_textures and current_path != root_dir and current_path.is_dir():
                try:
                    remaining_items = os.listdir(current_root)
                    if len(remaining_items) == 1:
                        single_item = current_path / remaining_items[0]
                        if single_item.is_file() and single_item.suffix.lower() == ".texturemap":
                            shutil.rmtree(current_path)
                            print(f"[SINGLE TEXTURE DIR DELETED] {current_path}")
                            deleted_count += 2
                            continue
                except OSError as error:
                    print(f"[ERROR CHECKING SINGLE TEXTURE] {current_path}: {error}")

            # 4. Reguläre Dateibereinigung (Whitelist / Blacklist)
            if current_path.is_dir():
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
                            print(f"[ERROR] {file_path}: {error}")

            # 5. Komplett leere Ordner löschen
            try:
                if current_path.is_dir() and len(os.listdir(current_root)) == 0:
                    if current_path != root_dir:
                        os.rmdir(current_root)
                        print(f"[DIRECTORY DELETED] {current_root}")
                        deleted_count += 1
            except OSError as error:
                print(f"[ERROR DELETING DIR] {current_root}: {error}")

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
        parser.add_argument("--suffix", type=AssassinsCreedShadowsCleaner.parse_suffix_list, nargs="+", metavar="SUFFIXES",
                        help='Specify one suffix or a list, e.g. --suffix \'[".mesh", ".texturemap"]\'')
        parser.add_argument("--remove_single_textures", "--remove_single_texture",
                        dest="remove_single_textures",
                        type=AssassinsCreedShadowsCleaner.parse_boolean, default=False,
                        metavar="True|False",
                        help="Delete folders containing only one .texturemap file")
        parser.add_argument("--remove_dir_without_mesh",
                        dest="remove_dir_without_mesh",
                        type=AssassinsCreedShadowsCleaner.parse_boolean, default=False,
                        metavar="True|False",
                        help="Delete folders that do not contain any .mesh files")
        parser.add_argument("--remove_env_assets",
                        dest="remove_env_assets",
                        type=AssassinsCreedShadowsCleaner.parse_boolean, default=False,
                        metavar="True|False",
                        help="Delete folders containing a .mesh file smaller than 10KB")
        parser.add_argument("--file_size",
                        dest="file_size",
                        type=int, default=10,  # <-- default=10 statt default=False
                        help="Delete folders containing a .mesh file that is smaller than set value in KB")
        arguments = parser.parse_args()
        suffix_values = [suffix for suffix_group in (arguments.suffix or []) for suffix in suffix_group]
        suffix_values = suffix_values or AssassinsCreedShadowsCleaner.DEFAULT_SUFFIXES
        arguments.suffix = {suffix.lower() for suffix in suffix_values}
        return arguments


if __name__ == "__main__":
    arguments = AssassinsCreedShadowsCleaner.parse_arguments()
    total_deleted = AssassinsCreedShadowsCleaner(
        arguments.root_dir,
        listing=arguments.listing,
        suffixes=arguments.suffix,
        remove_single_textures=arguments.remove_single_textures,
        remove_dir_without_mesh=arguments.remove_dir_without_mesh,
        remove_env_assets=arguments.remove_env_assets,
        file_size=arguments.file_size,
    ).main()

    print(f"Total number of entries deleted: {total_deleted}")