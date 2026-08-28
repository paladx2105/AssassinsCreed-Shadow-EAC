# AssassinsCreed-Shadow-EAC


Cleans up the “Extract” folder from AnvilToolKit. Removes all unnecessary files and folders used for retexturing and modeling.



Usage:



python ACShadowCleaner.py --root_dir “Path” --listing white|black --suffix ‘[“.mesh”, “.textureset”, “.texturemap”]’ --remove_single_textures True|False



--root_dir: Root folder. (Usually .../.../Extract/) Automatically searches all subfolders



--listing: Set to “White” to mark the suffixes as ‘Whitelisted’ and to “Black” to mark them as ‘Blacklisted’. (“Whitelisted” removes all files not listed in ‘--suffix’, and “Blacklisted” deletes only those listed in '--suffix'



--suffix: Enter the required or unnecessary file extensions here (e.g., 654564_6541SDF6784.texturemap). Case is not sensitive 



--remove_single_textures: If set to “True,” the script will check one final time to see if a folder contains only a single ‘.texturemap’ file; if so, the file and folder will be deleted
