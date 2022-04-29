from __future__ import annotations

import socket
import time

from loguru import logger

from vlcsync.vlc_models import VlcConnectionError

VLC_PROMPT = b"> "


class VlcConn:
    def __init__(self, host, port, pid=None):
        self.pid = pid  # if local vlc
        self.port = port
        self.host = host
        logger.trace("Connect {0}", port)
        self.sock = socket.create_connection((host, self.port))
        self._recv_answer()

    def cmd(self, command: str) -> str:
        self.sock.send(f"{command}\r\n".encode())
        data = self._recv_answer()
        return data.decode().replace("> ", "").replace("\r\n", "")

    def _recv_answer(self):
        data = b''
        try:
            timeout = time.time() + 1
            while data[-2:] != VLC_PROMPT:
                if time.time() > timeout:
                    raise TimeoutError()
                data += self.sock.recv(1024)

        except ConnectionAbortedError:
            raise VlcConnectionError(f"Socket lost connection", self.pid)
        except (socket.timeout, TimeoutError):
            logger.trace(f"Data when timeout {data}")
            raise VlcConnectionError(f"Socket receive answer native timeout.", self.pid)

        return data

    def close(self):
        logger.trace("Close socket {0}...", self.host, self.port)
        try:
            self.sock.close()
        except:
            pass