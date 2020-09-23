import glob
import re
import shutil
from config import error_file_path, out_file_path, directories_path
import os

err_files = glob.glob(error_file_path)
out_files = glob.glob(out_file_path)

combined = err_files + out_files

directories = glob.glob(directories_path)

# Matches "-" followed by alphanumeric
pattern = re.compile("(-)[0-9]+")

for file in combined:
    match = pattern.search(file)
    job_id = match.group()[1:] # Removing "-" from beginning
    filename = file.split('\\')[-1]
    
    # Looping through folders to find match
    # Inefficient, but doesn't matter since not too many folders
    for folder in directories:
        if job_id in folder:
            # print(job_id, folder,"\n")
            new_path = "".join([folder,filename])
            # print("new_path", new_path, "\n")

            if os.path.exists(new_path):
                # If exists, copy only if newer
                if os.stat(file).st_mtime - os.stat(new_path).st_mtime > 1:
                    shutil.copy2(file, new_path)

            else:
                # Copy if doesn't exist
                shutil.copy2(file, new_path)

