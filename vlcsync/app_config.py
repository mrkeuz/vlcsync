from __future__ import annotations

from dataclasses import dataclass
from typing import Set

from vlcsync.vlc_state import VlcId


@dataclass
class AppConfig:
    extra_rc_hosts: Set[VlcId]
    no_local_discovery: bool
    no_timestamp_sync: bool
    volume_sync: bool
