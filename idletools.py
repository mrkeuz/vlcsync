import timeit

import cmd_utils


def get_user_idle() -> int:
    """ Idle is millis """
    try:
        return int(cmd_utils.out(['/usr/bin/xprintidle']))
    except:
        return 0


if __name__ == '__main__':
    print(timeit.timeit("get_user_idle()", globals=globals(), number=10) / 10)
