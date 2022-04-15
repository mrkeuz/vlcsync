from __future__ import annotations

import functools
from functools import cached_property
import getpass
import re
import socket
import timeit

from cached_property import cached_property_with_ttl
from func_timeout import func_set_timeout
from loguru import logger
import psutil
from psutil import Process

import cmd_utils

ACTIVE_WINDOW = ['/usr/bin/xdotool', 'getactivewindow', 'getwindowpid']

VLC_IFACE = "127.0.0.42"


def find_vlc_netstat():
    vlc_ports = {}
    for line in cmd_utils.out(["netstat", "-nltp4"]).split():
        if 'vlc' in line and VLC_IFACE in line:
            m = re.search(r':(\d+).+?(\d+)/vlc', line)

            pid_port = int(m.group(1))
            pid = int(m.group(2))

            vlc_ports[pid] = pid_port
    return vlc_ports


def find_vlc_psutil() -> dict[int, int]:
    vlc_ports = {}

    for p in _find_procs_by_name("vlc"):
        port = _telnet_port(p)
        if port:
            vlc_ports[p.pid] = port
            # print(f"Vlc found with pid {p.pid}... ")

    return vlc_ports


def _find_procs_by_name(name):
    """Return a list of processes matching 'name'."""
    ls = []
    for p in psutil.process_iter():
        if p.username() == getpass.getuser() and (
                name == p.name() or
                p.cmdline() and p.cmdline()[0] == name
        ):
            ls.append(p)
    return ls


def _telnet_port(proc: Process) -> int | None:
    for p_conn in proc.connections("tcp4"):
        if p_conn.status == 'LISTEN' and p_conn.laddr.ip == VLC_IFACE:
            return p_conn.laddr.port


class Vlc:
    def __init__(self, port):
        self._port = port

    def is_paused(self):
        return "state paused" in self._vlc_cmd("status")

    def get_time(self) -> int | None:
        if self.is_paused():
            return None

        logger.trace("Request get_time from {0}", self._port)
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
            data += self._s.recv(128)
        return data

    @cached_property
    def _s(self) -> socket.socket:
        logger.trace("Connect {0}", self._port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((VLC_IFACE, self._port))
        data = b''
        while not data.endswith(b"> "):
            data += sock.recv(128)
        return sock

    def close(self):
        logger.trace("Close socket {0}...", self._port)
        try:
            self._s.close()
        except:
            pass


class VlcProcs:
    def __init__(self):
        self._vlc_instances: dict[int, Vlc] = {}

    @cached_property_with_ttl(ttl=5)
    def all_vlc(self) -> dict[int, Vlc]:
        logger.trace("Compute all_vlc...")
        cur_vlc = find_vlc_psutil()

        # Remove missed
        for missed_pid in (self._vlc_instances.keys() - cur_vlc.keys()):
            self._vlc_instances.pop(missed_pid).close()

        # Populate if not exists
        for pid, port in cur_vlc.items():
            self._vlc_instances[pid] = self._vlc_instances.get(pid) or Vlc(port)

        return self._vlc_instances

    def main_vlc(self) -> Vlc | None:
        main_window_pid = cmd_utils.out(ACTIVE_WINDOW)
        if main_window_pid and main_window_pid.strip().isdigit():
            active_pid: int = int(main_window_pid.strip())
            if self.is_vlc(active_pid):
                return self.all_vlc.get(active_pid)

    @functools.lru_cache(maxsize=256)
    def is_vlc(self, pid):
        proc = psutil.Process(pid)
        return proc.name() == 'vlc' or self.vlc_cmdline(proc)

    @staticmethod
    def vlc_cmdline(proc) -> bool:
        for part in proc.cmdline():
            if 'vlc' in part:
                return True
        return False

    def close(self):
        for vlc in self._vlc_instances.values():
            vlc.close()

        self._vlc_instances.clear()

    def __del__(self):
        self.close()


@functools.lru_cache(maxsize=128)
def cmd_name():
    print(psutil.Process(2855054).cmdline())


if __name__ == '__main__':
    n = 22
    print(timeit.timeit("cmd_name()", globals=globals(), number=n) / n)
