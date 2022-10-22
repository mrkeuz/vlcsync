import os
import shlex
import subprocess as sp
import time
import unittest

from vlcsync.vlc import VLC_IFACE_IP

from tests.helpers.geometry_utils import Geom, apply_geom_for
from tests.helpers.video_samples import generate_vid_sample
from vlcsync.vlc_finder import LocalProcessFinderProvider

geoms = {
    "test1.mp4": Geom(100, 100, "500x400"),
    "test2.mp4": Geom(1000, 100, "500x400"),
    "test3.mp4": Geom(600, 550, "600x400"),
}


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.system("killall vlc")
        samples = [generate_vid_sample("test1"),
                   generate_vid_sample("test2"),
                   generate_vid_sample("test3")]

        self.procs = [sp.Popen(shlex.split(f"vlc --rc-host 127.0.0.42 {sample}"))
                      for sample in samples]

        time.sleep(1)

        finder = LocalProcessFinderProvider(VLC_IFACE_IP)
        vlcs = finder.get_vlc_list()
        # WIP



    def test_something(self):
        time.sleep(3000)
        self.assertEqual(True, True)  # add assertion here

    def tearDown(self) -> None:
        for proc in self.procs:
            proc.kill()


if __name__ == '__main__':
    unittest.main()
