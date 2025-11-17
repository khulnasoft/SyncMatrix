import syncmatrix

from .utils import get_output


@syncmatrix.flow(name="test")
def test_flow():
    return get_output()


@syncmatrix.flow(name="test")
def prod_flow():
    return get_output()
