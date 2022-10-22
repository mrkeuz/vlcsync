from __future__ import annotations

from typing import Set
from urllib.parse import urlparse

import click
from loguru import logger

from vlcsync.vlc_state import VlcId


def parse_url(_, __, values) -> Set[VlcId]:
    if values:
        return {
            parse_vlc_id(next_addr)
            for next_addr in values
        }
    else:
        return set()


def parse_vlc_id(addr: str) -> VlcId:
    try:
        parsed_url = urlparse('//' + addr)
        return VlcId(str(parsed_url.hostname), parsed_url.port)
    except ValueError as e:
        logger.debug("Parse error.", e)
        raise click.BadParameter(f'{addr} is invalid (cause {e})') from e
    except Exception as e:
        error_msg = f'Unexpected error during parse {addr} (cause {e})'
        logger.error(error_msg)
        raise click.BadParameter(f'Unexpected error during parse {addr} (cause {e})') from e
