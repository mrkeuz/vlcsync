import timeit

from vlc_util import find_vlc_netstat, find_vlc_psutil


# Ps_utils 0.069
def test_ps_utils():
    find_vlc_psutil()


# Prev 0.032
def test_netstat():
    find_vlc_netstat()


def bench_find_vlc(f):
    n = 10
    bench = timeit.timeit(f, globals=globals(), number=n) / n
    print(f"Bench {f}: {bench:.3f} sec")


if __name__ == '__main__':
    bench_find_vlc("test_ps_utils()")
    bench_find_vlc("test_netstat()")
