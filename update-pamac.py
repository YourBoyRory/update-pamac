#!/bin/python

import os
import json
import shutil
import subprocess
import warnings
import argparse

BUILD_DIR = f"/tmp/pamac_build_{os.getuid()}"
PAMAC_OPTIONS_DIR = "/etc/install-pamac-options/"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--clean-build",
    action="store_true",
    help="Clean build dir before running"
)
parser.add_argument(
    "--dont-keep",
    action="store_true",
    help="Clean build dir after running"
)
parser.add_argument(
    "--force",
    action="store_true",
    help="Skips update check and reinstalls programs."
)
args = parser.parse_args()

with open(f"{PAMAC_OPTIONS_DIR}/pamac-options.json", "r") as f:
    data = json.load(f)
os.makedirs(BUILD_DIR, exist_ok=True)  # creates all missing folders
os.chdir(BUILD_DIR)



# Configure
for package, options in data.items():
    if args.clean_build and os.path.exists(package) and os.path.isdir(package):
        shutil.rmtree(package)
    subprocess.run(["yay", "-G", package])

    file_path = f"{package}/PKGBUILD"
    if os.path.exists(file_path) and os.path.isdir(package):
        # Set options
        for option, value in options.items():
            with open(file_path, "r") as f:
                lines = f.readlines()
            with open(file_path, "w") as f:
                for line in lines:
                    if line.startswith(f"{option}="):
                        new_line = f"{option}={value}"
                        if new_line != line.strip():
                            print(f"{line.strip()} -> {new_line}")
                            line = f"{option}={value}\n"
                        else:
                            print(f"{new_line} already set.")
                    f.write(line)
    else:
        warnings.warn(f"{file_path} done not exist", RuntimeWarning)

# Install
for package in data:
    if not args.force:
        result = subprocess.run(
            ["yay", "-Qu", package],
            capture_output=True,
            text=True
        )
        updates = result.stdout.strip()
        error = result.stderr.strip()
        code = result.returncode
    else:
        code = 0
        updates = "Forcing Updates"
    if code == 0 and updates:
        if os.path.exists(package) and os.path.isdir(package):
            subprocess.run(["makepkg", "-si"], cwd=package)
            if args.dont_keep:
                shutil.rmtree(package)
    elif code in [0,1] and not error:
        print(package, "is up to date!")
    else:
        print(f"\n{error}\n\n")
        sys.exit(code)

