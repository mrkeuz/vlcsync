from __future__ import annotations

import socket
import time

from cached_property import cached_property_with_ttl
from loguru import logger

from vlcsync.vlc_finder import VlcFinder
from vlcsync.vlc_conn import VlcConn

from vlcsync.vlc_models import PlayState, State

VLC_IFACE_IP = "127.0.0.42"

socket.setdefaulttimeout(0.5)


class Vlc:
    def __init__(self, pid, port):
        self.pid = pid
        self._port = port
        self.vlc_conn = VlcConn(VLC_IFACE_IP, port, pid)
        self.prev_state: State = self.cur_state()

    def play_state(self) -> PlayState:
        status = self.vlc_conn.cmd("status")
        return self._extract_state(status)

    def get_time(self) -> int | None:
        logger.trace("Request get_time from {0}", self._port)
        seek = self.vlc_conn.cmd("get_time")
        if seek != '':
            return int(seek)

    def seek(self, seek: int):
        self.vlc_conn.cmd(f"seek {seek}")

    def cur_state(self) -> State:
        get_time = self.get_time()

        return State(self.play_state(),
                     get_time,
                     time.time() - (get_time or 0))

    def is_state_change(self) -> (bool, State):
        cur_state: State = self.cur_state()
        prev_state: State = self.prev_state
        is_change = not cur_state.same(prev_state)

        # Return cur_state for reduce further socket communications
        return is_change, cur_state

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

        self.prev_state = self.cur_state()

    def pause_if_play(self, new_state, cur_play_state):
        if cur_play_state == PlayState.PLAYING and new_state.play_state == PlayState.PAUSED:
            self.vlc_conn.cmd("pause")

    def play_if_pause(self, new_state, cur_play_state):
        if cur_play_state == PlayState.PAUSED and new_state.play_state == PlayState.PLAYING:
            self.vlc_conn.cmd("play")

    @staticmethod
    def _extract_state(status, _valid_states=(PlayState.PLAYING.value,
                                              PlayState.PAUSED.value,
                                              PlayState.STOPPED.value)):
        for pb_state in _valid_states:
            if pb_state in status:
                return PlayState(pb_state)
        else:
            return PlayState.UNKNOWN

    def __repr__(self):
        return f"Vlc({self.pid=}, {self._port=}, {self.prev_state=})"

    def close(self):
        self.vlc_conn.close()


class VlcProcs:
    def __init__(self):
        self._vlc_instances: dict[int, Vlc] = {}
        self.vlcFinder = VlcFinder()

    @cached_property_with_ttl(ttl=5)
    def all_vlc(self) -> dict[int, Vlc]:
        start = time.time()

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

        logger.debug(f"Compute all_vlc (took {time.time() - start:.3f})...")
        return self._vlc_instances

    def sync_all(self, state: State, source: Vlc):
        logger.debug(">" * 60)
        logger.debug(f"Detect change to {state} from {source.pid}")
        logger.debug(f" old --> {source.prev_state} ")
        logger.debug(f" new --> {state} ")
        logger.debug(f" Time diff abs(old - new) {abs(state.time_diff - source.prev_state.time_diff)}")
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
