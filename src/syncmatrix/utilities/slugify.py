# Allows syncmatrix to be used side-by-side with unicode-slugify
# See https://github.com/KhulnaSoft/syncmatrix/issues/6945

from slugify import slugify

__all__ = ["slugify"]
