import re
import timeit
from typing import Callable, Iterable

from vlcsync.vlc_finder import VlcFinder
from vlcsync.vlc_util import VLC_IFACE_IP
from vlcsync.vlc_models import PlayState

finder = VlcFinder()


# Ps_utils 0.069
def bench_finder_utils():
    vlc_ports = {}
    for p in finder._find_vlc_procs():
        port = finder._has_listen_port(p, VLC_IFACE_IP)
        if port:
            vlc_ports[p.pid] = port
    vlc_ports


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


def bench_f(f: Callable, n=10) -> (int, str):
    assert callable(f), f"Arg {f=} should callable"
    try:
        bench = timeit.timeit(f, globals=globals(), number=n) / n
    except NotImplementedError:
        bench = 0

    return bench, f.__name__


def suite(tests: Iterable[Callable], n=10):
    results = {bench_f(test) for test in tests}
    offset = max([len(test.__name__) for test in tests]) + 5

    for bench, f in sorted(results):
        print(f"Bench {f:{offset}}: {bench:.6f} sec")
    print()


if __name__ == '__main__':
    suite([
        bench_finder_utils
    ])

    suite([
        bench_index,
        bench_in,
        bench_re,
        bench_in_enum,
        bench_in_cached
    ], n=100)
