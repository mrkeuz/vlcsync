from __future__ import annotations

import sys
import time
from typing import Set

import click

from vlcsync.cli_utils import parse_url
from vlcsync.syncer import AppConfig, Syncer
from vlcsync.vlc_finder import print_exc
from vlcsync.vlc_state import VlcId


@click.command
@click.option("--rc-host",
              'rc_host_list',
              help='Additional players (can be multiple)',
              required=False,
              callback=parse_url,
              multiple=True,
              metavar='<host:port>')
@click.option("--no-local-discover",
              "no_local_discover",
              required=False,
              is_flag=True,
              help="Disable discover local vlc instances")
def main(rc_host_list: Set[VlcId], no_local_discover):
    print("Vlcsync started...")

    app_config = AppConfig(rc_host_list, no_local_discover)
    time.sleep(2)  # Wait instances
    while True:
        try:
            with Syncer(app_config) as s:
                while True:
                    s.do_sync()
                    time.sleep(0.05)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception:
            print_exc()
            print("Exception detected. Restart sync...")