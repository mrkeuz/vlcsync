from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List

from loguru import logger

MAX_DESYNC_SECONDS = 4
"""
Tip:
Sometimes (on win + smb) delay increased/decreased randomly without change position in timeline
Possible vlc somehow does tricky synchronization during playing

Side by side playing same video visually appear asynchronous for little time
then it returns into normal synchronous.

In vlc preference by default enabled option "skip frames"
Max 4 second diff calculated empirically
"""


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
    playlist_order_idx: int
    # Real clock time of video start
    start_at_abs_time: float = field(repr=False)

    def same(self, other: State):
        return (self.same_play_state(other) and
                self.same_playlist_item(other) and
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
        desync_secs = abs(self.start_at_abs_time - other.start_at_abs_time)

        if 2 < desync_secs < MAX_DESYNC_SECONDS:
            logger.debug(f"Asynchronous anomaly between probes: {desync_secs} secs")

        return (
                self.play_state == other.play_state == PlayState.PLAYING and
                # self.start_at and other.start_at and
                desync_secs < MAX_DESYNC_SECONDS
        )

    def both_stopped(self, other: State):
        return self.play_state == other.play_state == PlayState.STOPPED

    def is_play_or_pause(self):
        return self.play_state in [PlayState.PLAYING, PlayState.PAUSED]

    def same_playlist_item(self, other):
        return self.playlist_order_idx == other.playlist_order_idx


@dataclass
class PlayListItem:
    order_index: int
    vlc_internal_index: int


@dataclass
class PlayList:
    items: List[PlayListItem]
    active_item: Optional[PlayListItem]

    def active_order_index(self) -> Optional[int]:
        return self.active_item.order_index if self.active_item else None


@dataclass(frozen=True)
class VlcId:
    addr: str
    port: int
    pid: Optional[int] = field(compare=False, hash=False, default=None)

    def __str__(self):
        return f"{self.addr}:{self.port}" + (f" (pid={self.pid})" if self.pid else "")
