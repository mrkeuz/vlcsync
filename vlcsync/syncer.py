from __future__ import annotations

from dataclasses import dataclass
import sys
import time
from typing import Set, List

from loguru import logger

from vlcsync.vlc import VLC_IFACE_IP, VlcProcs, Vlc
from vlcsync.vlc_finder import LocalProcessFinderProvider, ExtraHostFinder
from vlcsync.vlc_socket import VlcConnectionError

from vlcsync.vlc_state import VlcId


@dataclass
class AppConfig:
    extra_rc_hosts: Set[VlcId]
    no_local_discovery: bool
    no_timestamp_sync: bool
    volume_sync: bool


class Syncer:
    def __init__(self, app_config: AppConfig):
        self.env = None
        self.app_config = app_config
        self.supress_log_until = 0

        vlc_finders = set()
        if not self.app_config.no_local_discovery:
            vlc_finders.add(LocalProcessFinderProvider(VLC_IFACE_IP))
            print(f"  Discover instances on {VLC_IFACE_IP} iface...", flush=True)
        else:
            print("  Local discovery vlc instances DISABLED...", flush=True)

        if app_config.extra_rc_hosts:
            vlc_finders.add(ExtraHostFinder(app_config.extra_rc_hosts))
            for rc_host in app_config.extra_rc_hosts:
                rc_host: VlcId
                print(f"  Manual host defined {rc_host.addr}:{rc_host.port}", flush=True)
        else:
            print("""  Manual vlc addresses ("--rc-host" args) NOT provided...""", flush=True)

        if not vlc_finders:
            print("\nTarget vlc instances not selected (nor autodiscover, nor manually). \n"
                  """See: "vlcsync --help" for more info""", flush=True)
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
            is_changed, state, playlist_changed = vlc.is_state_change()

            if is_changed:
                # Workaround Save volumes.
                # When playlist items changed ALSO happen volumes sync by some reason. But SHOULD NOT!
                volumes: List[tuple[Vlc, int]] = []
                if not self.app_config.volume_sync and playlist_changed:
                    volumes = [(vlc1, vlc1.volume()) for _, vlc1 in self.env.all_vlc.items()]

                print(f"\nVlc state change detected from ({vlc_id})", flush=True)
                self.env.sync_all(state, vlc, self.app_config)

                # Restore volumes if needed
                if volumes:
                    for vlc_next, volume in volumes:
                        vlc_next.set_volume(volume)
                # Trying to fix endless resyncing hang
                # Cannot find reproduce steps for that
                time.sleep(0.5)
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
