#!/usr/bin/env -S python3 -u
from __future__ import annotations

from cached_property import cached_property_with_ttl
from func_timeout import func_set_timeout

from functools import cached_property
import socket
import subprocess
import sys
import time
import traceback

from loguru import logger

from ps_utils import VLC_IFACE, find_vlc_netstat, find_vlc_psutil

LINE_END = "\n"


class Vlc:
    def __init__(self, port):
        self._port = port

    def get_time(self) -> int | None:
        seek = self._vlc_cmd("get_time")
        if seek != '':
            return int(seek)

    def seek(self, seek):
        self._vlc_cmd(f"seek {seek}")

    @func_set_timeout(0.5)
    def _vlc_cmd(self, command) -> str:
        self._s.send(f"{command}\r\n".encode())
        data = self._recv_answer()
        return data.decode().replace("> ", "").replace("\r\n", "")

    def _recv_answer(self):
        data = b''
        while not data.endswith(b"> "):
            data += self._s.recv(1)
        return data

    @cached_property
    def _s(self) -> socket.socket:
        logger.debug(f"Connect {self._port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((VLC_IFACE, self._port))
        data = b''
        while not data.endswith(b"> "):
            data += sock.recv(1)
        return sock

    def close(self):
        self._s.close()

    def __del__(self):
        logger.debug(f"Close socket {self._port}...")
        self.close()


class Syncer:
    def __enter__(self):
        return Syncer()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @func_set_timeout(0.5)
    def do_sync(self):
        main_vlc = self._main_vlc

        if main_vlc is not None:
            seek = main_vlc.get_time()

            if seek is not None:
                for pid, next_vlc in self._all_vlc.items():
                    # Skip main
                    if main_vlc == next_vlc:
                        continue

                    # Skip stopped
                    if next_vlc.get_time() is None:
                        continue  # Skip player

                    if abs(seek - next_vlc.get_time()) > 2:
                        self._seek_all(seek)
                        break

    def _seek_all(self, seek):
        for sync_pid, sync_vlc in self._all_vlc.items():
            if sync_vlc.get_time() is not None:
                print(f"Sync {sync_pid} to {seek} from {sync_vlc.get_time()}...")
                sync_vlc.seek(seek)
        print()

    @property
    def _main_vlc(self):
        main_window = subprocess.getoutput("xdotool getactivewindow getwindowpid getwindowname")
        if main_window and main_window.endswith(" VLC"):
            active_pid = int(main_window.split()[0].strip())
            return self._all_vlc.get(int(active_pid))

    @cached_property_with_ttl(ttl=5)
    def _all_vlc(self) -> dict[int, Vlc]:
        all_vlc = {}
        for k, port in find_vlc_psutil().items():
            all_vlc[k] = Vlc(port)

        return all_vlc

    def close(self):
        for vlc in self._all_vlc.values():
            vlc.close()


def print_exc():
    print("-" * 60)
    print("Exception in user code: ")
    print("-" * 60)
    traceback.print_exc(file=sys.stdout)
    print("-" * 60)
    print()


if __name__ == '__main__':
    print("F1 syncronizer started...")
    time.sleep(2)  # Wait instances

    while True:
        try:
            with Syncer() as s:
                while True:
                    s.do_sync()
                    time.sleep(0.1)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print_exc()
            print("Exception detected. Restart sync...")
