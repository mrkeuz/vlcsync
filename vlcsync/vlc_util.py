from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
import socket
import time
from typing import Optional

from cached_property import cached_property_with_ttl
from loguru import logger

from vlcsync.utils import VlcFinder

VLC_IFACE_IP = "127.0.0.42"
from enum import Enum


class PlayState(Enum):
    PLAYING = "playing"
    STOPPED = "stopped"
    PAUSED = "paused"
    UNKNOWN = None

    @classmethod
    def _missing_(cls, value):
        return PlayState.UNKNOWN

    def __repr__(self):
        return self.value


@dataclass
class State:
    play_state: PlayState
    seek: int
    time_diff: float = field(repr=False)

    def same(self, other: State):
        return (self.same_play_state(other) and
                (
                        self.play_in_same_pos(other) or
                        self.pause_is_same_pos(other) or
                        self.both_stopped(other)
                )
                )

    def same_play_state(self, other: State):
        return self.play_state == other.play_state

    def pause_is_same_pos(self: State, other: State):
        return self.play_state == other.play_state == PlayState.PAUSED and self.seek == other.seek

    def play_in_same_pos(self: State, other: State):
        """ Check time_diff only when play """
        return (
                self.play_state == other.play_state == PlayState.PLAYING and
                self.time_diff and other.time_diff and
                abs(self.time_diff - other.time_diff) < 2
        )

    def both_stopped(self, other: State):
        return self.play_state == other.play_state == PlayState.STOPPED

    def is_active(self):
        return self.play_state in [PlayState.PLAYING, PlayState.PAUSED]


class Vlc:
    def __init__(self, pid, port):
        self.pid = pid
        self._port = port
        self.prev_state: State = self.cur_state()

    def play_state(self) -> PlayState:
        status = self._vlc_cmd("status")
        return self._extract_state(status)

    @staticmethod
    def _extract_state(status, _valid_states=(PlayState.PLAYING.value,
                                              PlayState.PAUSED.value,
                                              PlayState.STOPPED.value)):
        for pb_state in _valid_states:
            if pb_state in status:
                return PlayState(pb_state)
        else:
            return PlayState.UNKNOWN

    def get_time(self) -> int | None:
        logger.trace("Request get_time from {0}", self._port)
        seek = self._vlc_cmd("get_time")
        if seek != '':
            return int(seek)

    def seek(self, seek):
        self._vlc_cmd(f"seek {seek}")

    def cur_state(self) -> State:
        get_time = self.get_time()

        return State(self.play_state(),
                     get_time,
                     time.time() - (get_time or 0))

    def is_state_change(self) -> (bool, State):
        state = self.cur_state()
        is_change = not state.same(self.prev_state)

        # Return state for reduce further socket communications
        return is_change, state

    def sync_to(self, new_state: State, source: Vlc):
        if not new_state.is_active():
            return

        cur_play_state = self.play_state()

        if cur_play_state != new_state.play_state:
            self.play_if_pause(new_state, cur_play_state)
            self.pause_if_play(new_state, cur_play_state)

        # Sync all secondary, but main only when playing
        if source != self or cur_play_state == PlayState.PLAYING:
            self.seek(new_state.seek)

        self.prev_state = new_state

    def pause_if_play(self, new_state, cur_play_state):
        if cur_play_state == PlayState.PLAYING and new_state.play_state == PlayState.PAUSED:
            self._vlc_cmd("pause")

    def play_if_pause(self, new_state, cur_play_state):
        if cur_play_state == PlayState.PAUSED and new_state.play_state == PlayState.PLAYING:
            self._vlc_cmd("play")

    def _vlc_cmd(self, command: str) -> str:
        self._s.send(f"{command}\r\n".encode())
        data = self._recv_answer(self._s)
        return data.decode().replace("> ", "").replace("\r\n", "")

    def _recv_answer(self, sock: socket.socket):
        data = sock.recv(1024)
        timeout = time.time() + 1
        while data[-2:] != b"> ":
            if time.time() > timeout:
                raise VlcTimeoutError(f"Socket receive answer timeout.", self.pid)
            data += sock.recv(1024)
        return data

    @cached_property
    def _s(self) -> socket.socket:
        logger.trace("Connect {0}", self._port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((VLC_IFACE_IP, self._port))
        self._recv_answer(sock)
        return sock

    def __repr__(self):
        return f"Vlc({self.pid=}, {self._port=}, {self.prev_state=})"

    def close(self):
        logger.trace("Close socket {0}...", self._port)
        try:
            self._s.close()
        except:
            pass


class VlcProcs:
    def __init__(self):
        self.main_vlc: Optional[Vlc] = None
        self._vlc_instances: dict[int, Vlc] = {}
        self.vlcFinder = VlcFinder()

    @cached_property_with_ttl(ttl=2)
    def all_vlc(self) -> dict[int, Vlc]:
        logger.trace("Compute all_vlc...")
        vlc_in_system = self.vlcFinder.find_vlc(VLC_IFACE_IP)

        # Remove missed
        for missed_pid in (self._vlc_instances.keys() - vlc_in_system.keys()):
            self.dereg(missed_pid)

        # Populate if not exists
        for pid, port in vlc_in_system.items():
            if pid not in self._vlc_instances.keys():
                vlc = Vlc(pid, port)
                print(f"Found instance with pid {pid} and port {VLC_IFACE_IP}:{port} {vlc.cur_state()}")
                self._vlc_instances[pid] = vlc

        return self._vlc_instances

    def sync_all(self, state: State, source: Vlc):
        logger.debug(">" * 60)
        logger.debug(f"Detect change to {state} from {source.pid}")
        logger.debug(f" old --> {source.prev_state} ")
        logger.debug(f" new --> {state} ")
        logger.debug("<" * 60)
        logger.debug("")
        print(">>> Sync windows...")
        if not state.is_active():
            print("   Source window stopped. Skip sync")
            return

        for next_pid, next_vlc in self.all_vlc.items():
            next_vlc: Vlc
            if next_vlc.cur_state().is_active():
                print(f"    Sync {next_pid} to {state}")
                next_vlc.sync_to(state, source)
        print()

    def dereg(self, pid: int):
        print(f"Detect vlc instance closed pid {pid}")
        self._vlc_instances.pop(pid).close()

    def close(self):
        for vlc in self._vlc_instances.values():
            vlc.close()

        self._vlc_instances.clear()

    def __del__(self):
        self.close()


class VlcTimeoutError(TimeoutError):
    def __init__(self, msg: str, pid: int):
        super().__init__(msg)
        self.pid = pid
