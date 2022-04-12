#!/usr/bin/env python3
from __future__ import annotations

from functools import cached_property
import re
import socket
import subprocess
import sys
import time
import traceback

LINE_END = "\n"


class Vlc:
    def __init__(self, port):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = "127.0.0.1"
        self._s.connect((host, port))
        self._recv_answer()

    def get_time(self) -> int | None:
        seek = self._vlc_cmd("get_time")
        if seek != '':
            return int(seek)

    def seek(self, seek):
        self._vlc_cmd(f"seek {seek}")

    def _vlc_cmd(self, command) -> str:
        self._s.send(f"{command}\r\n".encode())
        data = self._recv_answer()
        return data.decode().replace("> ", "").replace("\r\n", "")

    def _recv_answer(self):
        data = b''
        while not data.endswith(b"> "):
            data += self._s.recv(1)
        return data

    def close(self):
        self._s.close()


class Syncer:
    def __enter__(self):
        return Syncer()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def do_sync(self):
        if self._main_vlc is not None:
            seek = self._main_vlc.get_time()

            if seek is not None:
                for pid, next_vlc in self._all_vlc.items():
                    # Skip main
                    if self._main_vlc == next_vlc:
                        continue

                    # Skip stopped
                    if next_vlc.get_time() is None:
                        continue  # Skip player

                    if abs(seek - next_vlc.get_time()) > 2:
                        self._sync_all(seek)
                        break

    def _sync_all(self, seek):
        for sync_pid, sync_vlc in self._all_vlc.items():
            if sync_vlc.get_time() is not None:
                print(f"Sync {sync_pid} to {seek} from {sync_vlc.get_time()}...")
                sync_vlc.seek(seek)
        print()

    @cached_property
    def _main_vlc(self):
        active_pid = subprocess.getoutput("xdotool getactivewindow getwindowpid")
        window_name = subprocess.getoutput("xdotool getactivewindow getwindowname")
        if re.fullmatch(r"^\d+$", active_pid) is not None and window_name.find("VLC") > 0:
            return self._all_vlc.get(int(active_pid))

    @cached_property
    def _all_vlc(self) -> dict[int, Vlc]:
        proc = subprocess.Popen(["netstat", "-nlp4"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        vlc_ports = {}

        for line in proc.stdout.readlines():
            if line.find(b'vlc') > 0 and line.find(b'127.0.0.1') > 0:
                m = re.search(r':(\d+).+?(\d+)/vlc', line.decode())

                pid_port = int(m.group(1))
                pid = int(m.group(2))

                vlc_ports[pid] = Vlc(pid_port)

        return vlc_ports

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

    # s = Syncer()
    # my_vlc: Vlc = list(s._all_vlc.values())[0]
    # print(my_vlc.get_time())

    while True:
        try:
            with Syncer() as s:
                s.do_sync()

            time.sleep(0.1)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print_exc()
