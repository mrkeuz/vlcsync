""" WIP For testing"""
import subprocess
import time
from pathlib import WindowsPath

from vlc_finder import VlcFinder

mkv = WindowsPath(
    "//192.168.1.104/nas2/Video/TopGear/TopGear Season 1-22/Season 19 (Jetvis Studio)/"
    "Top.Gear.19x06 Спецвыпуск В поисках истока Нила 1.mkv")


def start_vlc():
    return subprocess.Popen(["C:\\Program Files\\VideoLAN\\VLC\\vlc.exe", str(mkv.absolute())])


if __name__ == '__main__':
    start_vlc()
    time.sleep(600)

    # print(mkv.exists())
    # for par in mkv.parents:
    #     print(f"{par.absolute()} - {par.exists()}")
    #     # if par.exists() and "Video" in str(par.absolute()):
    #     #     print("*" * 60)
    #     #     for inner in par.iterdir():
    #     #         print(inner)
