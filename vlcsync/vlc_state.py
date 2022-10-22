from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

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
        desync_secs = abs(self.time_diff - other.time_diff)

        if 2 < desync_secs < MAX_DESYNC_SECONDS:
            logger.debug(f"Asynchronous anomaly between probes: {desync_secs} secs")

        return (
                self.play_state == other.play_state == PlayState.PLAYING and
                self.time_diff and other.time_diff and
                desync_secs < MAX_DESYNC_SECONDS
        )

    def both_stopped(self, other: State):
        return self.play_state == other.play_state == PlayState.STOPPED

    def is_active(self):
        return self.play_state in [PlayState.PLAYING, PlayState.PAUSED]


@dataclass(frozen=True)
class VlcId:
    addr: str
    port: int
    pid: Optional[int] = field(compare=False, hash=False, default=None)

    def __str__(self):
        return f"{self.addr}:{self.port}" + (f" (pid={self.pid})" if self.pid else "")
