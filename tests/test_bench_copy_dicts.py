orig = {1: "a", 2: "dsadsa", 3: "123"}


def test_bench_copy_dict(benchmark):
    benchmark(orig.copy)
