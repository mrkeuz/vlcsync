#!/usr/bin/env -S python3 -u
from __future__ import annotations

import os
import sys
import time

from loguru import logger

from vlcsync.utils import print_exc
from vlcsync.vlc_util import VlcProcs, VlcTimeoutError

if lvl := os.getenv("DEBUG_LEVEL"):
    logger.remove()
    logger.add(sys.stderr, level=lvl)
else:
    logger.remove()


class Syncer:
    def __init__(self):
        self.next_log = 0
        self.env = VlcProcs()

    def __enter__(self):
        syncer = Syncer()
        syncer.do_sync()
        return syncer

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def do_sync(self):
        self.log_with_debounce("Sync...")
        try:
            for pid, vlc in self.env.all_vlc.items():
                is_changed, state = vlc.is_state_change()
                if not state.is_active():
                    continue

                if is_changed:
                    print(f"\nVlc state change detected from {pid=}")
                    self.env.sync_all(state, vlc)
                    return

        except VlcTimeoutError as e:
            self.env.dereg(e.pid)

    def log_with_debounce(self, msg: str, _debounce=5):
        if time.time() > self.next_log:
            logger.debug(msg)
            self.next_log = time.time() + _debounce

    def __del__(self):
        self.close()

    def close(self):
        self.env.close()


def main():
    print("Vlcsync started...")
    time.sleep(2)  # Wait instances
    while True:
        try:
            with Syncer() as s:
                while True:
                    s.do_sync()
                    time.sleep(0.05)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print_exc()
            print("Exception detected. Restart sync...")


if __name__ == '__main__':
    main()
