from __future__ import annotations

import cmd_utils

_idle_fun = None


def _dummy_idle() -> int:
    """ I.e. for simple Windows, while idle not implemented """
    return 0


def _xprintidle_cffi() -> int:
    from xprintidle import idle_time
    return idle_time()


def _xprintidle_cmd() -> int:
    """ Idle is millis """
    return int(cmd_utils.out(['xprintidle']))


def user_idle_millis() -> int:
    global _idle_fun

    # Find fast and valid idle function
    if not _idle_fun:
        for f in [_xprintidle_cffi, _xprintidle_cmd, _dummy_idle]:
            try:
                f()  # should not raise
                _idle_fun = f
                break
            except:
                pass

        if _idle_fun == _dummy_idle:
            print("WARNING: Idle function not found (xprintidle or libx11-dev/libxss-dev).")

    return _idle_fun()


if __name__ == '__main__':
    print(user_idle_millis())
