from __future__ import annotations

import socket
import time

from loguru import logger

from vlcsync.vlc_state import VlcId

VLC_PROMPT = b"> "


class VlcSocket:
    def __init__(self, vlc_id: VlcId):
        self.vlc_id = vlc_id
        logger.trace("Connect {0}", vlc_id)
        self.sock = socket.create_connection((vlc_id.addr, vlc_id.port))
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._recv_answer()

    def cmd(self, command: str) -> str:
        logger.trace(f">>> Send {command=} to {self.vlc_id}")
        self.sock.send(f"{command}\r\n".encode())
        data = self._recv_answer()
        answer = data.decode().replace("> ", "").replace("\r\n", "")
        logger.trace(f"<<< Receive {answer=} from {self.vlc_id}")
        return answer

    def _recv_answer(self):
        data = b''
        try:
            timeout = time.time() + 1
            while data[-2:] != VLC_PROMPT:
                if time.time() > timeout:
                    raise TimeoutError()
                data += self.sock.recv(1024)

        except ConnectionAbortedError as e:
            raise VlcConnectionError(f"Socket lost connection", self.vlc_id) from e
        except (socket.timeout, TimeoutError) as e:
            logger.trace(f"Data when timeout {data}")
            raise VlcConnectionError(f"Socket receive answer native timeout.", self.vlc_id) from e
        except OSError as e:
            raise VlcConnectionError(f"Unexpected socket error.", self.vlc_id) from e

        return data

    def close(self):
        logger.trace("Close socket {0}...", self.vlc_id)
        try:
            self.sock.close()
        except Exception:
            pass


class VlcConnectionError(TimeoutError):
    def __init__(self, msg: str, vlc_id: VlcId):
        super().__init__(msg)
        self.vlc_id = vlc_id
