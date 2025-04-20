from __future__ import annotations

import sys
import time
from typing import Set

import click

from vlcsync.cli_utils import parse_url
from vlcsync.syncer import AppConfig, Syncer
from vlcsync.vlc_finder import print_exc
from vlcsync.vlc_state import VlcId

# Also ref in project.toml
__version__ = "0.3.1"


@click.command
@click.version_option(__version__)
@click.option("--rc-host",
              'rc_host_list',
              help='Additional players (can be multiple).',
              required=False,
              callback=parse_url,
              multiple=True,
              metavar='<host:port>')
@click.option("--no-local-discovery",
              "no_local_discover",
              required=False,
              is_flag=True,
              help="Disable discovery local vlc instances.")
@click.option("--volume-sync",
              "volume_sync",
              default=False,
              required=False,
              is_flag=True,
              help=
              """
              Enable volume sync between players. Useful for play video with external audio file.\n
              I.e. first play video with disabled audio track ('vlc --no-audio video.mkv' option) and then play audio stream (`vlc audio.mka`).
              \n  
              And you can control volume from main video player.
              """)
def main(rc_host_list: Set[VlcId], no_local_discover, volume_sync):
    """Utility for synchronize multiple instances of VLC. Supports seek, play and pause."""
    print("Vlcsync started...")

    app_config = AppConfig(rc_host_list, no_local_discover, volume_sync)
    time.sleep(2)  # Wait instances
    while True:
        try:
            with Syncer(app_config) as s:
                while True:
                    s.do_check_synchronized()
                    time.sleep(0.05)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception:
            print_exc()
            print("Exception detected. Restart sync...")
