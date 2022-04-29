from __future__ import annotations

import functools
import getpass
import sys
import traceback
from typing import Dict

import psutil
from psutil import Process

from contextlib import contextmanager


@contextmanager
def skip_on_error():
    try:
        yield
    except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
        # whatever your common handling is


class VlcFinder:
    def __init__(self):
        self.netstat_fail = False

    def find_vlc(self, iface) -> Dict[int, int]:
        vlc_ports = {}

        for proc in self._find_vlc_procs():
            port = self._has_listen_port(proc, iface)
            if port:
                vlc_ports[proc.pid] = port

        return vlc_ports

    def _find_vlc_procs(self):
        """Return a list of processes matching 'name'."""
        ls = []
        for p in psutil.process_iter():
            with skip_on_error():
                if self.is_vlc(p) and self.cur_user_own(p):
                    ls.append(p)

        return ls

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def cur_user_own(p) -> bool:
        with skip_on_error():
            is_user_own = getpass.getuser() in p.username()
            return is_user_own

        # noinspection PyUnreachableCode
        return False

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def _has_listen_port(proc: Process, iface_ip) -> int | None:
        with skip_on_error():
            for p_conn in proc.connections("tcp4"):
                if p_conn.status == 'LISTEN' and p_conn.laddr.ip == iface_ip:
                    return p_conn.laddr.port

        # noinspection PyUnreachableCode
        return None

    @functools.lru_cache(maxsize=1024)
    def is_vlc(self, proc: Process):
        with skip_on_error():
            return proc.name() == 'vlc' or self.vlc_cmdline(proc)

        # noinspection PyUnreachableCode
        return False

    @staticmethod
    def vlc_cmdline(proc) -> bool:
        for part in proc.cmdline():
            if 'vlc' in part:
                return True
        return False


def print_exc():
    print("-" * 60)
    print("Exception in user code: ")
    print("-" * 60)
    traceback.print_exc(file=sys.stdout)
    print("-" * 60)
    print()
