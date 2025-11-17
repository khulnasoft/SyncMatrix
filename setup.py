from setuptools import find_packages, setup

install_requires = [
    "click",
    # 'cloudpickle > 0.3.1',  # support for pickling loggers was added after 0.3.1
    "croniter",
    "cryptography",
    "distributed >= 1.16.1",
    "graphviz",
    "jsonpickle",
    "mypy_extensions",
    "python-dateutil",
    "requests",
    "wrapt",
    "toml",
    "typing",
    "typing_extensions",
    # "xxhash",
]

extras = {"dev": ["pytest", "pytest-env", "pytest-xdist"]}

setup(
    name="syncmatrix",
    # corresponds to __version__
    version="0.2.1",
    description="",
    long_description=open("README.md").read(),
    url="https://www.github.com/khulnasoft/syncmatrix",
    author="Md Sulaiman",
    author_email="dev.sulaiman@icloud.com",
    install_requires=install_requires,
    extras_require=extras,
    scripts=[],
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["syncmatrix=syncmatrix.cli:cli"]},
)
