#!/usr/bin/env -S python3 -u
from __future__ import annotations

import os
import sys

from loguru import logger

from vlcsync.cli import main

if lvl := os.getenv("DEBUG_LEVEL"):
    logger.remove()
    logger.add(sys.stderr, level=lvl)
else:
    logger.remove()

if __name__ == '__main__':
    main()
