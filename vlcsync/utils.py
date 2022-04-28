from __future__ import annotations

import functools
import getpass
import re
import sys
import traceback
from typing import Dict

import psutil
from psutil import Process

from vlcsync import cmd_utils


class VlcFinder:
    def __init__(self):
        self.netstat_fail = False

    def find_vlc(self, iface) -> Dict[int, int]:
        # More fast method but require netstat
        if not self.netstat_fail:
            try:
                return self.find_vlc_netstat(iface)
            except FileNotFoundError:
                self.netstat_fail = True
                print_exc()

        # Slow method
        return self.find_vlc_psutil(iface)

    @staticmethod
    def find_vlc_netstat(iface: str) -> Dict[int, int]:
        vlc_ports: Dict[int, int] = {}
        for line in cmd_utils.out(["netstat", "-nltp4"]).splitlines():
            if 'vlc' in line and iface in line:
                m = re.search(r':(\d+).+?(\d+)/vlc', line)

                pid_port = int(m.group(1))
                pid = int(m.group(2))

                vlc_ports[pid] = pid_port
        return vlc_ports

    def find_vlc_psutil(self, iface_ip: str) -> dict[int, int]:
        vlc_ports = {}

        for p in self._find_procs_by_name("vlc"):
            port = self._telnet_port(p, iface_ip)
            if port:
                vlc_ports[p.pid] = port

        return vlc_ports

    def _find_procs_by_name(self, name):
        """Return a list of processes matching 'name'."""
        ls = []
        for p in psutil.process_iter():
            if p.username() == getpass.getuser() and self.is_vlc(p):
                ls.append(p)
        return ls

    @staticmethod
    def _telnet_port(proc: Process, iface_ip) -> int | None:
        for p_conn in proc.connections("tcp4"):
            if p_conn.status == 'LISTEN' and p_conn.laddr.ip == iface_ip:
                return p_conn.laddr.port

    @functools.lru_cache(maxsize=256)
    def is_vlc(self, proc: Process):
        return proc.name() == 'vlc' or self.vlc_cmdline(proc)

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
