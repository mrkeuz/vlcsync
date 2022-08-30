from unittest import TestCase

from vlcsync.vlc import VLC_IFACE_IP
from vlcsync.vlc_finder import LocalProcessFinderProvider


class TestVlcFinder(TestCase):
    def test_find_vlc_psutil(self):
        finder = LocalProcessFinderProvider()
        vlc_ports = {}
        for p in finder._find_vlc_procs():
            port1 = finder._has_listen_port(p, VLC_IFACE_IP)
            if port1:
                vlc_ports[p.pid] = port1
        for pid, port in vlc_ports.items():
            print(f"Found {pid=} {port=}")
