"""
This module implements the Syncmatrix context that is available when tasks run.

Tasks can import syncmatrix.context and access attributes that will be overwritten
when the task is run.

Example:
    import syncmatrix.context
    with syncmatrix.context(a=1, b=2):
        print(syncmatrix.context.a) # 1
    print (syncmatrix.context.a) # undefined

"""

import contextlib
from typing import Any, Iterator, MutableMapping

from syncmatrix.utilities.collections import DotDict


class Context(DotDict):
    """
    A context store for Syncmatrix data.
    """

    def __repr__(self) -> str:
        return "<Context>"

    @contextlib.contextmanager
    def __call__(self, *args: MutableMapping, **kwargs: Any) -> Iterator["Context"]:
        """
        A context manager for setting / resetting the Syncmatrix context

        Example:
            import syncmatrix.context
            with syncmatrix.context(dict(a=1, b=2), c=3):
                print(syncmatrix.context.a) # 1
        """
        previous_context = self.copy()
        try:
            self.update(*args, **kwargs)
            yield self
        finally:
            self.clear()
            self.update(previous_context)


context = Context()
