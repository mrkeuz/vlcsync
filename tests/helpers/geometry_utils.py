from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import functools
import re
from typing import Optional

from vlcsync.cmd_utils import out


@dataclass
class Geom:
    x: int
    y: int
    w_h: str

    @property
    def width(self):
        return self.w_h.split("x")[0]

    @property
    def height(self):
        return self.w_h.split("x")[1]

def apply_geom_for(window_title: str, geom: Geom):
    for wid in out(f"xdotool search --onlyvisible --name 'VLC'").splitlines():
        wind_name = out(f"""xdotool getwindowname "{wid}" """)
        if window_title in wind_name:
            out(f"xdotool windowsize {wid} {geom.width} {geom.height}")
            out(f"xdotool windowmove {wid} {geom.x} {geom.y}")


def rearrange(dev: str):
    for wid in out(f"xdotool search --onlyvisible --name 'VLC'").splitlines():
        wind_name = out(f"""xdotool getwindowname "{wid}" """)
        # geom = out(f"""xdotool getwindowgeometry "{wid}" """)
        # print(f"  wid {wid} - {wind_name} ({geom})")

        # Move
        g = geom_for_window(wind_name, dev)
        if g:
            out(f"xdotool windowsize {wid} {g.width} {g.height}")
            out(f"xdotool windowmove {wid} {g.x} {g.y}")


def _geom_for_window(window_name: str, dev="dev") -> Optional[Geom]:
    for regex, geom in geom_list(dev).items():
        if re.search(regex, window_name):
            return geom

    return None


def _geom_list(dev: str) -> OrderedDict[str, Geom]:
    geom = OrderedDict()
    if dev == "dev":
        geom["Data.Channel"] = Geom(4520, 100, "500x400")
        geom["Driver.Tracker"] = Geom(3978, 100, "500x400")
        geom[".+"] = Geom(4248, 550, "600x400")
    if dev == "F1":
        geom["Data.Channel"] = Geom(1, 75, "1920x1043")
        geom["Driver.Tracker"] = Geom(3841, 75, "1280x987")
        geom[".+"] = Geom(1921, 106, "1920x946")
    return geom


if __name__ == '__main__':
    rearrange("dev")

