from __future__ import annotations

from functools import cached_property
import socket

from func_timeout import func_set_timeout
from loguru import logger

from ps_utils import VLC_IFACE


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
