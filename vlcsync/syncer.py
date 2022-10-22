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
        self.do_sync()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def do_sync(self):
        self.log_with_debounce("Sync...")
        try:
            for vlc_id, vlc in self.env.all_vlc.items():
                is_changed, state = vlc.is_state_change()
                if not state.is_active():
                    continue

                if is_changed:
                    print(f"\nVlc state change detected from ({vlc_id})")
                    self.env.sync_all(state, vlc)
                    return

        except VlcConnectionError as e:
            self.env.dereg(e.vlc_id)

    def log_with_debounce(self, msg: str, _debounce=5):
        if time.time() > self.supress_log_until:
            logger.debug(msg)
            self.supress_log_until = time.time() + _debounce

    def __del__(self):
        self.close()

    def close(self):
        if self.env:
            self.env.close()
