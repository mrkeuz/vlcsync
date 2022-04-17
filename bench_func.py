import re
import timeit

from utils import VlcFinder
from vlc_util import VLC_IFACE_IP, PlayState

finder = VlcFinder()


# Ps_utils 0.069
def test_ps_utils():
    finder.find_vlc_psutil(VLC_IFACE_IP)


# Prev 0.032
def test_netstat():
    finder.find_vlc_netstat(VLC_IFACE_IP)


def bench_find_vlc(f, n=10):
    bench = timeit.timeit(f, globals=globals(), number=n) / n

    return bench, f


status = "ioqewufpodia state pause"


def bench_index():
    # Indexed
    start = status.find("state ", 21)
    sub = status[start + 6:start + 6 + 2]
    if sub == 'pl':
        return PlayState.PLAYING
    elif sub == 'pa':
        return PlayState.PAUSED
    elif sub == 'st':
        return PlayState.STOPPED
    else:
        return PlayState.UNKNOWN


e_list = [PlayState.PLAYING.value, PlayState.STOPPED.value, PlayState.PAUSED.value]
re_state = "state ({0})".format("|".join(e_list))
re_state_compiled = re.compile(re_state)


def bench_re():
    match = re_state_compiled.search(status)

    return PlayState(match.group(1)) if match else PlayState.UNKNOWN


def bench_in():
    for pb_state in e_list:
        if pb_state in status:
            return PlayState(pb_state)
    else:
        return PlayState.UNKNOWN


def bench_in_cached(_valid_states=(PlayState.PLAYING.value,
                                   PlayState.PAUSED.value,
                                   PlayState.STOPPED.value)):
    for pb_state in _valid_states:
        if pb_state in status:
            return PlayState(pb_state)
    else:
        return PlayState.UNKNOWN


def bench_in_enum():
    for pb_state in PlayState:
        # print(pb_state)
        if (pb_state.value or "unk") in status:
            return pb_state
    else:
        return PlayState.UNKNOWN


if __name__ == '__main__':
    for bench, f in sorted([bench_find_vlc("test_ps_utils()"),
                            bench_find_vlc("test_netstat()")]):
        print(f"Bench {f:20}: {bench:.3f} sec")

    print()

    results = [bench_find_vlc("bench_index()"),
               bench_find_vlc("bench_re()"),
               bench_find_vlc("bench_in_enum()"),
               bench_find_vlc("bench_in()"),
               bench_find_vlc("bench_in_cached()")]

    for bench, f in sorted(results):
        print(f"Bench {f:20}: {bench:.9f} sec")
