import versioneer
from setuptools import find_packages, setup

client_requires = open("requirements-client.txt").read().strip().split("\n")
# strip the first line since setup.py will not recognize '-r requirements-client.txt'
install_requires = (
    open("requirements.txt").read().strip().split("\n")[1:] + client_requires
)
dev_requires = open("requirements-dev.txt").read().strip().split("\n")

setup(
    # Package metadata
    name="syncmatrix",
    description="Workflow orchestration and management.",
    author="KhulnaSoft",
    author_email="supports@khulnasoft.com",
    url="https://www.khulnasoft.com",
    project_urls={
        "Changelog": "https://github.com/KhulnaSoft/syncmatrix/blob/main/RELEASE-NOTES.md",
        "Documentation": "https://docs.syncmatrix.io",
        "Source": "https://github.com/KhulnaSoft/syncmatrix",
        "Tracker": "https://github.com/KhulnaSoft/syncmatrix/issues",
    },
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # Package setup
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    # CLI
    entry_points={
        "console_scripts": ["syncmatrix=syncmatrix.cli:app"],
        "mkdocs.plugins": [
            "render_swagger = syncmatrix.utilities.render_swagger:SwaggerPlugin",
        ],
    },
    # Requirements
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={"dev": dev_requires},
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
    ],
)