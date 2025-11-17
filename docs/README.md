# Syncmatrix

## Welcome to Syncmatrix!

Syncmatrix is a workflow management system designed for modern data infrastructures.

Users organize `tasks` into `flows`, and Syncmatrix takes care of the rest!


### "...Syncmatrix?"

From the Latin *praefectus*, meaning "one who is in charge", a syncmatrix is an official who oversees a domain and ensures that the rules are followed.

It also happens to be the name of a roving researcher for that wholly remarkable book, *The Hitchhiker's Guide to the Galaxy*.


## Installation

### Requirements

Syncmatrix requires Python 3.4+.

### Install
```
git clone https://gitlab.com/syncmatrix/syncmatrix.git
cd syncmatrix
pip install .
```


## Development

### Install

```bash
git clone https://gitlab.com/syncmatrix/syncmatrix.git
cd syncmatrix
pip install -e ".[dev]"
# pre-commit install
```

<!-- ### Pre-commit
Syncmatrix enforces [Black](https://github.com/ambv/black) and
[isort](https://github.com/timothycrosley/isort) formatting on every commit, using
[pre-commit](https://pre-commit.com/). If a commit violates a pre-commit requirement,
the commit will fail and the responsible files will be updated automatically. The
changes can then be recommitted successfully.

For example, if a modified file doesn't conform to Black standards, the commit will fail
(and the error message should indicate why). Black will automatically be run on the file
to fix any errors, and another attempt to commit will be successful. -->

### Unit Tests

```bash
cd syncmatrix
pytest
```

## Documentation

To build and view documentation:
```bash
yarn docs:dev
```
This will automatically open a new browser window, but there will be a slight delay
while the initial build finishes. When it finishes, the browser will automatically
refresh.
