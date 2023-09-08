from __future__ import annotations

from dataclasses import dataclass
import sys
import time
from typing import Set

from loguru import logger

from vlcsync.vlc import VLC_IFACE_IP, VlcProcs
from vlcsync.vlc_finder import LocalProcessFinderProvider, ExtraHostFinder
from vlcsync.vlc_socket import VlcConnectionError

from vlcsync.vlc_state import VlcId


@dataclass
class AppConfig:
    extra_rc_hosts: Set[VlcId]
    no_local_discovery: bool
    volume_sync: bool


class Syncer:
    def __init__(self, app_config: AppConfig):
        self.env = None
        self.app_config = app_config
        self.supress_log_until = 0

        vlc_finders = set()
        if not self.app_config.no_local_discovery:
            vlc_finders.add(LocalProcessFinderProvider(VLC_IFACE_IP))
            print(f"  Discover instances on {VLC_IFACE_IP} iface...")
        else:
            print("  Local discovery vlc instances DISABLED...")

        if app_config.extra_rc_hosts:
            vlc_finders.add(ExtraHostFinder(app_config.extra_rc_hosts))
            for rc_host in app_config.extra_rc_hosts:
                rc_host: VlcId
                print(f"  Manual host defined {rc_host.addr}:{rc_host.port}")
        else:
            print("""  Manual vlc addresses ("--rc-host" args) NOT provided...""")

        if not vlc_finders:
            print("\nTarget vlc instances not selected (nor autodiscover, nor manually). \n"
                  """See: "vlcsync --help" for more info""")
            sys.exit(1)

        self.env = VlcProcs(vlc_finders)

    def __enter__(self):
        self.do_check_synchronized()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def do_check_synchronized(self):
        self.log_with_debounce("do_check_synchronized()...")
        try:
            if self.app_config.volume_sync:
                self.sync_volume()

            self.sync_playstate()

        except VlcConnectionError as e:
            self.env.dereg(e.vlc_id)

    def sync_playstate(self):
        for vlc_id, vlc in self.env.all_vlc.items():
            is_changed, state = vlc.is_state_change()

            if is_changed:
                print(f"\nVlc state change detected from ({vlc_id})")
                self.env.sync_all(state, vlc)
                break

    def sync_volume(self):
        for vlc_id, vlc in self.env.all_vlc.items():
            cur_volume = vlc.volume()
            if vlc.prev_volume != cur_volume:
                for vlc_id_for_sync, vlc_for_sync in self.env.all_vlc.items():
                    vlc_for_sync.prev_volume = cur_volume
                    if vlc_for_sync != vlc:
                        vlc_for_sync.set_volume(cur_volume)
                break

    def log_with_debounce(self, msg: str, _debounce=5):
        if time.time() > self.supress_log_until:
            logger.debug(msg)
            self.supress_log_until = time.time() + _debounce

    def __del__(self):
        self.close()

    def close(self):
        if self.env:
            self.env.close()
