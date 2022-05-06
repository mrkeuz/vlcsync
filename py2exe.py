#!/usr/bin/env -S python3 -u
import os
import re


def get_version() -> str:
    with open("./pyproject.toml", "r") as f:
        read = f.read()
        version = re.search(r'version = "(.+?)"', read)
        if version and version.group(0):
            return version.group(1)
        else:
            return "_latest"


if __name__ == '__main__':
    print(get_version())
    os.system(f"pyinstaller --specpath ./dist --onefile -n vlcsync_{get_version()} ./vlcsync/main.py")
