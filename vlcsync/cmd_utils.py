from __future__ import annotations

import getpass
import platform
import shlex
import subprocess
from functools import cached_property
from typing import List

LINUX_ENV = {
    "DISPLAY": ":0",
    "XDG_RUNTIME_DIR": f"/run/user/{getpass.getuser()}",
}


class CmdTools:
    @cached_property
    def _env(self):
        if platform.system() == "Linux":
            return LINUX_ENV
        else:
            return {}

    def check_output(self, cmd_for_run: List[str]) -> bytes:
        return subprocess.check_output(cmd_for_run, shell=False, env=self._env, stderr=subprocess.DEVNULL)


cmd = CmdTools()


def out(command: List[str] | str) -> str:
    if isinstance(command, str):
        command = shlex.split(command)
    return cmd.check_output(command).decode()


if __name__ == '__main__':
    print(subprocess.check_output(shlex.split("ls -la")))
    print(out("ls -la"))
