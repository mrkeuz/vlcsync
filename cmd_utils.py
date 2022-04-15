from functools import cached_property
import os
import platform
import subprocess

from typing import List

LINUX_ENV = {
    "DISPLAY": ":0",
    "XDG_RUNTIME_DIR": f"/run/user/{os.getuid()}",
}


class CmdTools:
    @cached_property
    def _env(self):
        if platform.system() == "Linux":
            return LINUX_ENV
        else:
            return {}

    def get_output(self, cmd_for_run: List[str]) -> bytes:
        return subprocess.check_output(cmd_for_run, shell=False, env=self._env, stderr=subprocess.DEVNULL)


cmd = CmdTools()


def out(command: List[str]) -> str:
    return cmd.get_output(command).decode()
