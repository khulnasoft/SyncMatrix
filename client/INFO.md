# Overview

This directory contains files for building and publishing the `syncmatrix-client` 
library. `syncmatrix-client` is built by removing source code from `syncmatrix` and 
packages its own `requirements.txt` and `setup.py`. This process can happen 
in one of three ways:

- automatically whenever a PR is created (see 
`.github/workflows/syncmatrix-client.yaml`)
- automatically whenever a Github release is published (see 
`.github/workflows/syncmatrix-client-publish.yaml`)
- manually by running the `client/build_client.sh` script locally

Note that whenever a Github release is published the `syncmatrix-client` will 
not only get built but will also be distributed to PyPI. `syncmatrix-client` 
releases will have the same versioning as `syncmatrix` - only the package names 
will be different.

This directory also includes a "minimal" flow that is used for smoke 
tests to ensure that the built `syncmatrix-client` is functional.

In general, these builds, smoke tests, and publish steps should be transparent. 
It these automated steps fail, use the `client/build_client.sh` script to run 
the build and smoke test locally and iterate on a fix. The failures will likely 
be from:

- including a new dependency that is not installed in `syncmatrix-client`
- re-arranging or adding files in such a way that a necessary file is rm'd at 
  build time
