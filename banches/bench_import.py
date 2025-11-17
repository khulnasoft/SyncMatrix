import subprocess

from pytest_benchmark.fixture import BenchmarkFixture


def bench_import_syncmatrix(benchmark: BenchmarkFixture):
    benchmark.pedantic(
        subprocess.check_call, args=(["python", "-c", "import syncmatrix"],), rounds=5
    )