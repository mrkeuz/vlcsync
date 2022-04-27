from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import functools
import re
from typing import Optional

from cmd_utils import out


@dataclass
class WindGeom:
    x: int
    y: int
    w_h: str

    @property
    def width(self):
        return self.w_h.split("x")[0]

    @property
    def height(self):
        return self.w_h.split("x")[1]


def rearrange(dev: bool):
    for wid in out(f"xdotool search --onlyvisible --name 'VLC'").splitlines():
        wind_name = out(f"""xdotool getwindowname "{wid}" """)
        # geom = out(f"""xdotool getwindowgeometry "{wid}" """)
        # print(f"  wid {wid} - {wind_name} ({geom})")

        # Move
        g = geom_for_window(wind_name, dev)
        if g:
            out(f"xdotool windowsize {wid} {g.width} {g.height}")
            out(f"xdotool windowmove {wid} {g.x} {g.y}")


@functools.lru_cache(maxsize=6)
def geom_for_window(window_name: str, dev: True) -> Optional[WindGeom]:
    for regex, geom in geom_list(dev).items():
        if re.search(regex, window_name):
            return geom

    return None


@functools.lru_cache(maxsize=2)
def geom_list(dev) -> OrderedDict[str, WindGeom]:
    geom = OrderedDict()
    if dev:
        geom["Data.Channel"] = WindGeom(4520, 100, "500x400")
        geom["Driver.Tracker"] = WindGeom(3978, 100, "500x400")
        geom[".+"] = WindGeom(4248, 550, "600x400")
    else:
        geom["Data.Channel"] = WindGeom(1, 75, "1920x1043")
        geom["Driver.Tracker"] = WindGeom(3841, 75, "1280x987")
        geom[".+"] = WindGeom(1921, 106, "1920x946")
    return geom


if __name__ == '__main__':
    rearrange(True)
