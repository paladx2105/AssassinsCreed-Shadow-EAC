# AssassinsCreed-Shadow-EAC

A powerful Python utility designed for automated cleaning and filtering of extracted game assets (such as 3D models, textures, and folder structures) from *Assassin's Creed Shadows*.

---

## 📖 Table of Contents
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
  - [Basic Command](#basic-command)
  - [Command-Line Arguments](#command-line-arguments)
- [Examples](#-examples)
  - [1. Default Whitelist Cleanup](#1-default-whitelist-cleanup)
  - [2. Remove Directories Without 3D Models (.mesh)](#2-remove-directories-without-3d-models-mesh)
  - [3. Filter Environment Assets (Small Meshes)](#3-filter-environment-assets-small-meshes)
  - [4. Delete Isolated Texture Folders](#4-delete-isolated-texture-folders)
  - [5. Blacklist Mode (Targeted Deletion)](#5-blacklist-mode-targeted-deletion)
- [Execution Order](#-execution-order)
- [Notes & Safety Warnings](#-notes--safety-warnings)

---

## 🛠 Features

- **Whitelist & Blacklist Filtering:**
  - **Whitelist Mode (Default):** Retains only specified file extensions (e.g., `.mesh`, `.texture`, `.textureset`, `.texturemap`) and removes all other files.
  - **Blacklist Mode:** Deletes only specified file extensions while leaving others intact.
- **Remove Meshless Directories (`--remove_dir_without_mesh`):** Deletes entire directory trees if they do not contain any `.mesh` files.
- **Filter Environment Assets (`--remove_env_assets` & `--file_size`):** Detects and removes directories containing `.mesh` files smaller than a specified threshold (Default: `< 10 KB`) to filter out minor environmental/decorative assets.
- **Single Texture Folder Cleanup (`--remove_single_textures`):** Cleans up folders containing only a single `.texturemap` file.
- **Automatic Empty Directory Cleanup:** Removes remaining empty directories after files have been cleaned up.

---

## ⚙️ Prerequisites

- **Python 3.7+** (No third-party packages required — built entirely using standard Python libraries: `argparse`, `os`, `shutil`, `json`, `pathlib`).

---

## 📥 Installation

1. Save the script as `ac_shadows_cleaner.py` on your machine.
2. Open your Command Prompt, PowerShell, or Terminal.

---

## 🚀 Usage

### Basic Command

```bash
python ac_shadows_cleaner.py --root_dir "C:\path\to\extracted_assets"
```

---

### Command-Line Arguments

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--root_dir` | `Path` | *Required* | The root directory to scan and clean. |
| `--listing` | `white` \| `black` | `white` | **`white`**: Keep specified extensions, delete the rest.<br>**`black`**: Delete specified extensions, keep the rest. |
| `--suffix` | `List / String` | `[.mesh, .texture, .textureset, .texturemap]` | File extensions to include in whitelist/blacklist filtering. |
| `--remove_dir_without_mesh` | `True` \| `False` | `False` | Deletes directories that contain no `.mesh` files. |
| `--remove_env_assets` | `True` \| `False` | `False` | Deletes directories containing `.mesh` files smaller than `--file_size`. |
| `--file_size` | `Integer` | `10` | Size threshold in **KB** for `--remove_env_assets`. |
| `--remove_single_textures` | `True` \| `False` | `False` | Deletes directories containing only a single `.texturemap` file. |

---

## 💡 Examples

### 1. Default Whitelist Cleanup
Deletes all files in the directory tree that do **not** have `.mesh`, `.texture`, `.textureset`, or `.texturemap` extensions:

```bash
python ac_shadows_cleaner.py --root_dir "./extracted_files"
```

---

### 2. Remove Directories Without 3D Models (.mesh)
Removes subdirectories that do not contain any 3D mesh files after extraction:

```bash
python ac_shadows_cleaner.py --root_dir "./extracted_files" --remove_dir_without_mesh True
```

---

### 3. Filter Environment Assets (Small Meshes)
Removes folders whose `.mesh` files are smaller than 10 KB (or a user-defined threshold in KB):

```bash
python ac_shadows_cleaner.py --root_dir "./extracted_files" --remove_env_assets True --file_size 15
```

---

### 4. Delete Isolated Texture Folders
Deletes folders that contain only a single `.texturemap` file and no other assets:

```bash
python ac_shadows_cleaner.py --root_dir "./extracted_files" --remove_single_textures True
```

---

### 5. Blacklist Mode (Targeted Deletion)
Deletes specific unwanted file types (e.g., `.bin` and `.dat`) across the folder structure:

```bash
python ac_shadows_cleaner.py --root_dir "./extracted_files" --listing black --suffix '[".bin", ".dat"]'
```

---

## 🔄 Execution Order

The script traverses the directory tree bottom-up (**`topdown=False`**). This ensures deep subdirectories are processed first and empty folders are removed cleanly in sequence:

1. **Mesh Check:** Evaluates whether directories lacking `.mesh` files should be removed.
2. **Environment Asset Check:** Evaluates `.mesh` file sizes against the threshold (`--file_size`).
3. **Single Texture Check:** Detects and deletes folders containing only one `.texturemap`.
4. **Whitelist / Blacklist Filtering:** Deletes unwanted files based on specified suffixes.
5. **Empty Directory Removal:** Cleans up any remaining empty directories.

---

## ⚠️ Notes & Safety Warnings

- **Deletions are Permanent:** The script uses `os.remove` and `shutil.rmtree`. Deleted files are **not** moved to the Recycle Bin/Trash.
- **Backup Recommended:** Always create a backup of your extracted assets before running the script, or test it on a sample folder first.
