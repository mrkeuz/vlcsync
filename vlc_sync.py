#!/usr/bin/env -S python3 -u
from __future__ import annotations

import sys
import time
import traceback

from func_timeout import func_set_timeout
from loguru import logger
from profilehooks import timecall, profile

import idletools
from vlc_util import VlcProcs

logger.add(sys.stderr, level="INFO")
# logger.add(sys.stderr, level="TRACE")

LINE_END = "\n"


class Syncer:
    def __init__(self):
        self.vlc_proc = VlcProcs()

    def __enter__(self):
        return Syncer()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @profile
    @timecall(immediate=False)
    def do_sync(self):
        # Heuristics for reduce calls
        if idletools.get_user_idle() > 500:
            return

        main_vlc = self.vlc_proc.main_vlc()
        if main_vlc is None:
            return

        logger.trace("Do sync")
        seek = main_vlc.get_time()

        if seek is not None:
            for pid, next_vlc in self.vlc_proc.all_vlc.items():
                # Skip main
                if main_vlc == next_vlc:
                    continue

                # Skip stopped
                next_time = next_vlc.get_time()
                if next_time is None:
                    continue  # Skip player

                if abs(seek - next_time) > 2:
                    self._seek_all(seek)
                    break

    def _seek_all(self, seek):
        for sync_pid, sync_vlc in self.vlc_proc.all_vlc.items():
            if sync_vlc.get_time() is not None:  # Skip paused
                print(f"Sync {sync_pid} to {seek}...")
                sync_vlc.seek(seek)
        print()

    def __del__(self):
        self.close()

    def close(self):
        self.vlc_proc.close()


def print_exc():
    print("-" * 60)
    print("Exception in user code: ")
    print("-" * 60)
    traceback.print_exc(file=sys.stdout)
    print("-" * 60)
    print()


if __name__ == '__main__':
    print("F1 stream syncronizer started...")
    time.sleep(2)  # Wait instances

    while True:
        try:
            with Syncer() as s:
                while True:
                    s.do_sync()
                    time.sleep(0.1)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print_exc()
            print("Exception detected. Restart sync...")
