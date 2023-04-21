import random
import timeit
from typing import Callable, Iterable

from vlcsync.vlc import VLC_IFACE_IP, Vlc
from vlcsync.vlc_finder import LocalProcessFinderProvider
from vlcsync.vlc_state import PlayState

finder = LocalProcessFinderProvider(VLC_IFACE_IP)


# Ps_utils 0.069
def bench_finder_utils():
    vlc_ports = {}
    for p in finder._find_vlc_procs():
        port = finder._has_listen_port(p, VLC_IFACE_IP)
        if port:
            vlc_ports[p.pid] = port


status = "ioqewufpodia( state paused )"


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


def bench_extract_state_re():
    s = status
    Vlc._extract_state(s + str(random.randint(0, 100500)))

r = random.Random()
def bench_extract_playlist_re():
    s = """
    | 1 - Плейлист
    |   6 - Video 1.mkv (00:23:37) [played 1 time]
    |  *4 - Video 2.mkv (00:23:44) [played 2 times]
    |   3 - Video 3.mkv (00:23:43) [played 1 time]
    |   5 - Video 4.mkv (00:23:44) [played 1 time]
    | 2 - Медиатека
    |   12 - Video 6.mkv (00:23:44)
    +----[ End of playlist ]
    """
    Vlc._extract_playlist(s + str(random.randint(0, 100500)))


def bench_in():
    for pb_state in ['played', 'paused', 'stopped']:
        if pb_state in status:
            return PlayState(pb_state)

    return PlayState.UNKNOWN


def bench_in_cached(_valid_states=(PlayState.PLAYING.value,
                                   PlayState.PAUSED.value,
                                   PlayState.STOPPED.value)):
    for pb_state in _valid_states:
        if pb_state in status:
            return PlayState(pb_state)

    return PlayState.UNKNOWN


def bench_in_enum():
    for pb_state in PlayState:
        # print(pb_state)
        if (pb_state.value or "unk") in status:
            return pb_state

    return PlayState.UNKNOWN


def bench_f(f: Callable, n=10) -> (int, str):
    assert callable(f), f"Arg {f=} should callable"
    try:
        bench = timeit.timeit(f, globals=globals(), number=n) / n
    except NotImplementedError:
        bench = 0

    return bench, f.__name__


def suite(tests: Iterable[Callable], n=10):
    results = {bench_f(test, n) for test in tests}
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
        bench_extract_state_re,
        bench_extract_playlist_re,
        bench_in_enum,
        bench_in_cached
    ], n=100)
