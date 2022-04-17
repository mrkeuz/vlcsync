#!/usr/bin/env -S python3 -u
from __future__ import annotations

import sys
import time

from loguru import logger
from profilehooks import timecall, profile

from utils import print_exc
from vlc_util import VlcProcs, PlayState
from geometry_utils import rearrange

logger.remove()
# logger.add(sys.stderr, level="INFO")


class Syncer:
    def __init__(self):
        self.env = VlcProcs()

    def __enter__(self):
        return Syncer()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @profile
    def do_sync(self):
        for pid, vlc in self.env.all_vlc.items():
            sec_changed, sec_state = vlc.is_state_change()
            if not sec_state.is_active():
                continue

            if sec_changed:
                self.env.sync_all(sec_state, vlc)
                return

    def __del__(self):
        self.close()

    def close(self):
        self.env.close()


@timecall()
def main():
    print("F1 stream syncronizer started...")
    time.sleep(2)  # Wait instances
    rearrange(False)
    while True:
        try:
            with Syncer() as s:
                while True:
                    s.do_sync()
                    time.sleep(0.01)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print_exc()
            print("Exception detected. Restart sync...")


if __name__ == '__main__':
    main()
