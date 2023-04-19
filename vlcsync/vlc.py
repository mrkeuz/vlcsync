from __future__ import annotations

from functools import lru_cache
import re
import socket
import threading
import time
from typing import Set, List, Optional

from loguru import logger

from vlcsync.vlc_finder import IVlcListFinder
from vlcsync.vlc_socket import VlcSocket
from vlcsync.vlc_state import PlayState, State, VlcId, PlayList, PlayListItem

VLC_IFACE_IP = "127.0.0.42"

socket.setdefaulttimeout(0.5)


class Vlc:
    def __init__(self, vlc_id: VlcId):
        self.vlc_id = vlc_id
        self.vlc_conn = VlcSocket(vlc_id)
        self.prev_state: State = self.cur_state()

    def play_state(self) -> PlayState:
        status = self.vlc_conn.cmd("status")
        return self._extract_state(status)

    def get_time(self) -> int | None:
        seek = self.vlc_conn.cmd("get_time")
        if seek != '':
            return int(seek)

    def playlist_goto(self, vlc_internal_index: int):
        self.vlc_conn.cmd(f"goto {vlc_internal_index}")

    def playlist(self) -> PlayList:
        cmd_resp = self.vlc_conn.cmd("playlist")
        return self._extract_playlist(cmd_resp)

    def seek(self, seek: int):
        self.vlc_conn.cmd(f"seek {seek}")

    def stop(self):
        self.vlc_conn.cmd("stop")

    def cur_state(self) -> State:
        get_time = self.get_time()

        return State(self.play_state(),
                     get_time,
                     self.playlist().active_order_index(),
                     time.time() - (get_time or 0)
                     )

    def is_state_change(self) -> (bool, State):
        cur_state: State = self.cur_state()
        prev_state: State = self.prev_state
        is_change = not cur_state.same(prev_state)

        # Return cur_state for reduce further socket communications
        return is_change, cur_state

    def sync_to(self, new_state: State, source: Vlc):
        if new_state.play_state == PlayState.STOPPED:
            self.stop()

        if new_state.is_play_or_pause():
            self.sync_playlist(new_state)

        if new_state.is_play_or_pause():
            cur_play_state = self.play_state()

            if cur_play_state != new_state.play_state:
                self.play_if_pause(new_state, cur_play_state)
                self.pause_if_play(new_state, cur_play_state)

            if cur_play_state == PlayState.PAUSED and source == self:
                """
                Skip sync seek with himself on pause (avoid flickering)
                As half-seconds not supported and cannot to set.
                """
                pass
            else:
                # In all other cases
                self.seek(new_state.seek)

        self.prev_state = self.cur_state()

    def sync_playlist(self, new_state):
        cur_playlist = self.playlist()
        if cur_playlist.active_order_index() != new_state.playlist_order_idx:
            if new_state.playlist_order_idx is not None and len(cur_playlist.items) > new_state.playlist_order_idx:
                self.playlist_goto(cur_playlist.items[new_state.playlist_order_idx].vlc_internal_index)
            else:
                self.stop()

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

        return PlayState.UNKNOWN

    @staticmethod
    @lru_cache(maxsize=32)
    def _extract_playlist(resp: str) -> PlayList:
        """ Playlist Format
        +----[ Playlist - playlist ]
        | 1 - Плейлист
        |   6 - Video 1.mkv (00:23:37) [played 1 time]
        |  *4 - Video 2.mkv (00:23:44) [played 2 times]
        |   3 - Video 3.mkv (00:23:43) [played 1 time]
        |   5 - Video 4.mkv (00:23:44) [played 1 time]
        | 2 - Медиатека
        |   12 - Video 6.mkv (00:23:44)
        +----[ End of playlist ]
        """

        items: List[PlayListItem] = []
        active: Optional[PlayListItem] = None

        item_re = r'\| {2}([ \*])(\d+) -.'
        for idx, match in enumerate(re.finditer(item_re, resp)):
            item = PlayListItem(idx, match.group(2))
            items.append(item)
            if match.group(1) == "*":
                active = item

        return PlayList(items, active)

    def __repr__(self):
        return f"Vlc({self.vlc_id}, {self.prev_state=})"

    def close(self):
        self.vlc_conn.close()


class VlcProcs:
    def __init__(self, vlc_list_providers: Set[IVlcListFinder]):
        self.closed = False
        self._vlc_instances: dict[VlcId, Vlc] = {}
        self.vlc_list_providers = vlc_list_providers
        self.vlc_finder_thread = threading.Thread(target=self.refresh_vlc_list_periodically, daemon=True)
        self.vlc_finder_thread.start()

    def refresh_vlc_list_periodically(self):
        while not self.closed:
            start = time.time()

            vlc_candidates = []

            for vlc_list_provider in self.vlc_list_providers:
                vlc_list_provider: IVlcListFinder
                next_vlc_ids_list: Set[VlcId] = vlc_list_provider.get_vlc_list()

                vlc_candidates.extend(next_vlc_ids_list)
                logger.debug(next_vlc_ids_list)

            # Remove missed
            for orphaned_vlc in (self._vlc_instances.keys() - vlc_candidates):
                self.dereg(orphaned_vlc)

            # Populate if not exists
            for vlc_id in vlc_candidates:
                if vlc_id not in self._vlc_instances.keys():
                    if vlc := self.try_connect(vlc_id):
                        print(f"Found active instance {vlc_id}, with state {vlc.cur_state()}")
                        self._vlc_instances[vlc_id] = vlc

            logger.debug(f"Compute all_vlc (took {time.time() - start:.3f})...")
            time.sleep(5)

    @staticmethod
    def try_connect(vlc_id):
        try:
            return Vlc(vlc_id)
        except Exception as e:
            logger.opt(exception=True).debug("Cannot connect to {0}, cause: {1}", vlc_id, e)
            print(f"Cannot connect to {vlc_id} socket, cause: {e}. Skipping. Enable debug for more info. See --help. ")
            return None

    @property
    def all_vlc(self) -> dict[VlcId, Vlc]:
        return self._vlc_instances.copy()  # copy: for thread safe

    def sync_all(self, state: State, source: Vlc):
        logger.debug(">" * 60)
        logger.debug(f"Detect change to {state} from {source.vlc_id}")
        logger.debug(f" old --> {source.prev_state} ")
        logger.debug(f" new --> {state} ")
        logger.debug(f" Time diff abs(old - new) {abs(state.start_at_abs_time - source.prev_state.start_at_abs_time)}")
        logger.debug("<" * 60)
        logger.debug("")
        print(">>> Sync players...")

        for next_pid, next_vlc in self.all_vlc.items():
            next_vlc: Vlc
            print(f"    Sync {next_pid} to {state}")
            next_vlc.sync_to(state, source)
        print()

    def dereg(self, vlc_id: VlcId):
        print(f"Detect vlc instance closed {vlc_id}")
        if vlc_to_close := self._vlc_instances.pop(vlc_id, None):
            vlc_to_close.close()

    def close(self):
        for vlc in self._vlc_instances.values():
            vlc.close()

        self.closed = True
        self._vlc_instances.clear()

    def __del__(self):
        self.close()
