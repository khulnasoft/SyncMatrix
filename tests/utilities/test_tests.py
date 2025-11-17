import pytest

import syncmatrix

from syncmatrix.utilities.tests import raise_on_fail
from syncmatrix.core import Flow, Task
from syncmatrix.engine import TaskRunner


class BusinessTask(Task):
    def run(self):
        raise syncmatrix.signals.FAIL("needs more blockchain!")


class MathTask(Task):
    def run(self):
        1 / 0


def test_raise_on_fail_raises_basic_error():
    flow = Flow()
    flow.add_task(MathTask())
    with pytest.raises(ZeroDivisionError):
        with raise_on_fail():
            flow.run()


def test_raise_on_fail_raises_basic_syncmatrix_signal():
    flow = Flow()
    flow.add_task(BusinessTask())
    with pytest.raises(syncmatrix.signals.FAIL) as error:
        with raise_on_fail():
            flow.run()
    assert "needs more blockchain!" in str(error)


def test_raise_on_fail_works_at_the_task_level_with_error():
    taskrunner = TaskRunner(task=MathTask())
    with pytest.raises(ZeroDivisionError):
        with raise_on_fail():
            taskrunner.run()


def test_raise_on_fail_works_at_the_task_level_with_signal():
    taskrunner = TaskRunner(task=BusinessTask())
    with pytest.raises(syncmatrix.signals.FAIL) as error:
        with raise_on_fail():
            taskrunner.run()
    assert "needs more blockchain!" in str(error)


def test_core_code_errors_bubble_up(monkeypatch):
    flow = Flow()
    flow.add_task(MathTask())

    class BadTaskRunner(TaskRunner):
        def handle_fail(self, *args, **kwargs):
            raise RuntimeError("I'm not cool with this.")

    monkeypatch.setattr(syncmatrix.engine, "TaskRunner", BadTaskRunner)
    with pytest.raises(RuntimeError) as error:
        with raise_on_fail():
            flow.run()
    assert "I'm not cool with this." in str(error)


def test_raise_on_fail_raises_basic_error():
    flow = Flow()
    flow.add_task(MathTask())
    try:
        assert "_raise_on_fail" not in syncmatrix.context
        with raise_on_fail():
            assert "_raise_on_fail" in syncmatrix.context
            flow.run()
        assert "_raise_on_fail" not in syncmatrix.context
    except ZeroDivisionError:
        pass
