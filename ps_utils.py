from __future__ import annotations

import getpass
import re
import subprocess

from psutil import Process
import psutil as psutil

VLC_IFACE = "127.0.0.42"


def find_vlc_netstat():
    proc = subprocess.Popen(["netstat", "-nltp4"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    vlc_ports = {}
    for line in proc.stdout.readlines():
        if b'vlc' in line and VLC_IFACE.encode() in line:
            m = re.search(r':(\d+).+?(\d+)/vlc', line.decode())

            pid_port = int(m.group(1))
            pid = int(m.group(2))

            vlc_ports[pid] = pid_port
    return vlc_ports


def find_vlc_psutil() -> dict:
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
        if p_conn.status == 'LISTEN' and p_conn.laddr.ip == '127.0.0.42':
            return p_conn.laddr.port


if __name__ == '__main__':
    print(_find_procs_by_name("vlc"))
    print()
