from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, Iterable, TypeVar, Union

import syncmatrix
from syncmatrix.core import Flow, Task
from syncmatrix.engine.flow_runner import FlowRunner
from syncmatrix.engine.state import State
from syncmatrix.engine.task_runner import TaskRunner
from syncmatrix.utilities.json import Serializable


class Executor(Serializable):
    def __init__(self):
        pass

    @contextmanager
    def start(self):
        """
        This method is called
        """
        yield self

    def submit(self, fn, *args, **kwargs):
        """
        Submit a function to the executor for execution. Returns a future.
        """
        raise NotImplementedError()

    def wait(self, futures, timeout=None):
        """
        Resolves futures to their values. Blocks until the future is complete.
        """
        raise NotImplementedError()

    def set_state(
        self,
        current_state: State,
        state: State,
        data: Any = None,
        message: Union[str, Exception] = None,
    ) -> State:
        return state(data=data, message=message)

    def run_flow(
        self,
        flow: Flow,
        state: State,
        task_states: Dict[Task, State],
        start_tasks: Iterable[Task],
        return_tasks: Iterable[Task],
        parameters: Dict,
        context: Dict,
    ):
        context = context or {}
        context.update(syncmatrix.context)
        flow_runner = FlowRunner(flow=flow, executor=self)

        return self.submit(
            flow_runner.run,
            flow=flow,
            state=state,
            task_states=task_states,
            start_tasks=start_tasks,
            return_tasks=return_tasks,
            context=context,
            parameters=parameters,
        )

    def run_task(
        self,
        task: Task,
        state: State,
        upstream_states: Dict[Task, State],
        inputs: Dict[str, Any],
        ignore_trigger=False,
        context=None,
    ):
        context = context or {}
        context.update(syncmatrix.context)
        task_runner = syncmatrix.engine.TaskRunner(task=task, executor=self)

        return self.submit(
            task_runner.run,
            state=state,
            upstream_states=upstream_states,
            inputs=inputs,
            ignore_trigger=ignore_trigger,
            context=syncmatrix.context,
        )
