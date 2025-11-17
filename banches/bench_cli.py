import subprocess

from pytest_benchmark.fixture import BenchmarkFixture


def bench_syncmatrix_help(benchmark: BenchmarkFixture):
    benchmark.pedantic(subprocess.check_call, args=(["syncmatrix", "--help"],), rounds=3)


def bench_syncmatrix_version(benchmark: BenchmarkFixture):
    benchmark.pedantic(subprocess.check_call, args=(["syncmatrix", "version"],), rounds=3)


def bench_syncmatrix_short_version(benchmark: BenchmarkFixture):
    benchmark.pedantic(
        subprocess.check_call, args=(["syncmatrix", "--version"],), rounds=3
    )


def bench_syncmatrix_profile_ls(benchmark: BenchmarkFixture):
    benchmark.pedantic(
        subprocess.check_call, args=(["syncmatrix", "profile", "ls"],), rounds=3
    )