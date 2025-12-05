# Tasks

#### Versionadded

<a id="module-django.tasks"></a>

The Task framework provides the contract and plumbing for background work, not
the engine that runs it. The Tasks API defines how work is described, queued,
and tracked, but leaves actual execution to external infrastructure.

## Task definition

### The `task` decorator

### task(, priority=0, queue_name='default', backend='default', takes_context=False)

The `@task` decorator defines a [`Task`](#django.tasks.Task) instance. This has the
following optional arguments:

* `priority`: Sets the [`priority`](#django.tasks.Task.priority) of the `Task`. Defaults
  to 0.
* `queue_name`: Sets the [`queue_name`](#django.tasks.Task.queue_name) of the `Task`.
  Defaults to `"default"`.
* `backend`: Sets the [`backend`](#django.tasks.Task.backend) of the `Task`. Defaults to
  `"default"`.
* `takes_context`: Controls whether the `Task` function accepts a
  [`TaskContext`](#django.tasks.TaskContext). Defaults to `False`. See [Task context](../topics/tasks.md#task-context) for details.

If the defined `Task` is not valid according to the backend,
[`InvalidTask`](#django.tasks.exceptions.InvalidTask) is raised.

See [defining tasks](../topics/tasks.md#defining-tasks) for usage examples.

### `Task`

### *class* Task

Represents a Task to be run in the background. Tasks should be defined
using the [`task()`](#django.tasks.task) decorator.

Attributes of `Task` cannot be modified. See [modifying Tasks](../topics/tasks.md#modifying-tasks) for details.

#### priority

The priority of the `Task`. Priorities must be between -100 and 100,
where larger numbers are higher priority, and will be run sooner.

The backend must have [`supports_priority`](#django.tasks.backends.base.BaseTaskBackend.supports_priority) set to `True` to use
this feature.

#### backend

The alias of the backend the `Task` should be enqueued to. This must
match a backend defined in [`BACKEND`](settings.md#std-setting-TASKS-BACKEND).

#### queue_name

The name of the queue the `Task` will be enqueued on to. Defaults to
`"default"`. This must match a queue defined in
[`QUEUES`](settings.md#std-setting-TASKS-QUEUES), unless
[`QUEUES`](settings.md#std-setting-TASKS-QUEUES) is set to `[]`.

#### run_after

The earliest time the `Task` will be executed. This can be a
[`timedelta`](https://docs.python.org/3/library/datetime.html#datetime.timedelta), which is used relative to the
current time, a timezone-aware [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime),
or `None` if not constrained. Defaults to `None`.

The backend must have [`supports_defer`](#django.tasks.backends.base.BaseTaskBackend.supports_defer) set to `True` to use
this feature. Otherwise,
[`InvalidTask`](#django.tasks.exceptions.InvalidTask) is raised.

#### name

The name of the function decorated with [`task()`](#django.tasks.task). This name is not
necessarily unique.

#### using(, priority=None, backend=None, queue_name=None, run_after=None)

Creates a new `Task` with modified defaults. The existing `Task` is
left unchanged.

`using` allows modifying the following attributes:

* [`priority`](#django.tasks.Task.priority)
* [`backend`](#django.tasks.Task.backend)
* [`queue_name`](#django.tasks.Task.queue_name)
* [`run_after`](#django.tasks.Task.run_after)

See [modifying Tasks](../topics/tasks.md#modifying-tasks) for usage examples.

#### enqueue(\*args, \*\*kwargs)

Enqueues the `Task` to the `Task` backend for later execution.

Arguments are passed to the `Task`’s function after a round-trip
through a [`json.dumps()`](https://docs.python.org/3/library/json.html#json.dumps)/[`json.loads()`](https://docs.python.org/3/library/json.html#json.loads) cycle. Hence, all
arguments must be JSON-serializable and preserve their type after the
round-trip.

If the `Task` is not valid according to the backend,
[`InvalidTask`](#django.tasks.exceptions.InvalidTask) is raised.

See [enqueueing Tasks](../topics/tasks.md#enqueueing-tasks) for usage examples.

#### aenqueue(\*args, \*\*kwargs)

The `async` variant of [`enqueue`](#django.tasks.Task.enqueue).

#### get_result(result_id)

Retrieves a result by its id.

If the result does not exist, [`TaskResultDoesNotExist`](#django.tasks.exceptions.TaskResultDoesNotExist) is raised. If the
result is not the same type as the current Task,
[`TaskResultMismatch`](#django.tasks.exceptions.TaskResultMismatch)
is raised. If the backend does not support `get_result()`,
[`NotImplementedError`](https://docs.python.org/3/library/exceptions.html#NotImplementedError) is raised.

#### aget_result(\*args, \*\*kwargs)

The `async` variant of [`get_result`](#django.tasks.Task.get_result).

## Task context

### *class* TaskContext

Contains context for the running [`Task`](#django.tasks.Task). Context only passed to a
`Task` if it was defined with `takes_context=True`.

Attributes of `TaskContext` cannot be modified.

#### task_result

The [`TaskResult`](#django.tasks.TaskResult) currently being run.

#### attempt

The number of the current execution attempts for this Task, starting at
1.

## Task results

### *class* TaskResultStatus

An Enum representing the status of a [`TaskResult`](#django.tasks.TaskResult).

#### READY

The [`Task`](#django.tasks.Task) has just been enqueued, or is ready to be executed
again.

#### RUNNING

The [`Task`](#django.tasks.Task) is currently being executed.

#### FAILED

The [`Task`](#django.tasks.Task) raised an exception during execution, or was unable
to start.

#### SUCCESSFUL

The [`Task`](#django.tasks.Task) has finished executing successfully.

### *class* TaskResult

The `TaskResult` stores the information about a specific execution of a
[`Task`](#django.tasks.Task).

Attributes of `TaskResult` cannot be modified.

#### task

The [`Task`](#django.tasks.Task) the result was enqueued for.

#### id

A unique identifier for the result, which can be passed to
[`Task.get_result()`](#django.tasks.Task.get_result).

The format of the id will depend on the backend being used. Task result
ids are always strings less than 64 characters.

See [Task results](../topics/tasks.md#task-results) for more details.

#### status

The [`status`](#django.tasks.TaskResultStatus) of the result.

#### enqueued_at

The time when the `Task` was enqueued.

#### started_at

The time when the `Task` began execution, on its first attempt.

#### last_attempted_at

The time when the most recent `Task` run began execution.

#### finished_at

The time when the `Task` finished execution, whether it failed or
succeeded.

#### backend

The backend the result is from.

#### errors

A list of [`TaskError`](#django.tasks.TaskError) instances for the errors raised as part of
each execution of the Task.

#### return_value

The return value from the `Task` function.

If the `Task` did not finish successfully, [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError) is
raised.

See [return values](../topics/tasks.md#task-return-values) for usage examples.

#### refresh()

Refresh the result’s attributes from the queue store.

#### arefresh()

The `async` variant of [`TaskResult.refresh()`](#django.tasks.TaskResult.refresh).

#### is_finished

Whether the `Task` has finished (successfully or not).

#### attempts

The number of times the Task has been run.

If the task is currently running, it does not count as an attempt.

#### worker_ids

The ids of the workers which have executed the Task.

### Task errors

### *class* TaskError

Contains information about the error raised during the execution of a
`Task`.

#### traceback

The traceback (as a string) from the raised exception when the `Task`
failed.

#### exception_class

The exception class raised when executing the `Task`.

## Backends

Backends handle how Tasks are stored and executed. All backends share a common
interface defined by `BaseTaskBackend`, which specifies the core methods for
enqueueing Tasks and retrieving results.

### Base backend

### *class* BaseTaskBackend

`BaseTaskBackend` is the parent class for all Task backends.

#### options

A dictionary of extra parameters for the Task backend. These are
provided using the [`OPTIONS`](settings.md#std-setting-TASKS-OPTIONS) setting.

#### enqueue(task, args, kwargs)

Task backends which subclass `BaseTaskBackend` should implement this
method as a minimum.

When implemented, `enqueue()` enqueues the `task`, a [`Task`](#django.tasks.Task)
instance, for later execution. `args` are the positional arguments
and `kwargs` are the keyword arguments to be passed to the `task`.
Returns a [`TaskResult`](#django.tasks.TaskResult).

#### aenqueue(task, args, kwargs)

The `async` variant of [`BaseTaskBackend.enqueue()`](#django.tasks.backends.base.BaseTaskBackend.enqueue).

#### get_result(result_id)

Retrieve a result by its id. If the result does not exist,
[`TaskResultDoesNotExist`](#django.tasks.exceptions.TaskResultDoesNotExist) is raised.

If the backend does not support `get_result()`,
[`NotImplementedError`](https://docs.python.org/3/library/exceptions.html#NotImplementedError) is raised.

#### aget_result(result_id)

The `async` variant of [`BaseTaskBackend.get_result()`](#django.tasks.backends.base.BaseTaskBackend.get_result).

#### validate_task(task)

Validates whether the provided `Task` is able to be enqueued using
the backend. If the Task is not valid,
[`InvalidTask`](#django.tasks.exceptions.InvalidTask)
is raised.

#### Feature flags

Some backends may not support all features Django provides. It’s possible to
identify the supported functionality of a backend, and potentially change
behavior accordingly.

#### BaseTaskBackend.supports_defer

Whether the backend supports enqueueing Tasks to be executed after a
specific time using the [`run_after`](#django.tasks.Task.run_after) attribute.

#### BaseTaskBackend.supports_async_task

Whether the backend supports enqueueing async functions (coroutines).

#### BaseTaskBackend.supports_get_result

Whether the backend supports retrieving `Task` results from another
thread after they have been enqueued.

#### BaseTaskBackend.supports_priority

Whether the backend supports executing Tasks as ordered by their
[`priority`](#django.tasks.Task.priority).

The below table notes which of the [built-in backends](#task-available-backends) support which features:

| Feature                                                                                  | [`DummyBackend`](#django.tasks.backends.dummy.DummyBackend)   | [`ImmediateBackend`](#django.tasks.backends.immediate.ImmediateBackend)   |
|------------------------------------------------------------------------------------------|---------------------------------------------------------------|---------------------------------------------------------------------------|
| [`supports_defer`](#django.tasks.backends.base.BaseTaskBackend.supports_defer)           | Yes                                                           | No                                                                        |
| [`supports_async_task`](#django.tasks.backends.base.BaseTaskBackend.supports_async_task) | Yes                                                           | Yes                                                                       |
| [`supports_get_result`](#django.tasks.backends.base.BaseTaskBackend.supports_get_result) | No                                                            | No <sup>[1](#fnimmediateresult)</sup>                                     |
| [`supports_priority`](#django.tasks.backends.base.BaseTaskBackend.supports_priority)     | Yes <sup>[2](#fndummypriority)</sup>                          | Yes <sup>[3](#fnimmediatepriority)</sup>                                  |

<a id="task-available-backends"></a>

### Available backends

Django includes only development and testing backends. These support local
execution and inspection, for production ready backends refer to
[Configuring a Task backend](../topics/tasks.md#configuring-a-task-backend).

#### Immediate backend

### *class* ImmediateBackend

The [immediate backend](../topics/tasks.md#immediate-task-backend) executes Tasks
immediately, rather than in the background.

#### Dummy backend

### *class* DummyBackend

The [dummy backend](../topics/tasks.md#dummy-task-backend) does not execute enqueued
Tasks. Instead, it stores task results for later inspection.

#### results

A list of results for the enqueued Tasks, in the order they were
enqueued.

#### clear()

Clears the list of stored results.

## Exceptions

### *exception* InvalidTask

Raised when the [`Task`](#django.tasks.Task) attempting to be enqueued
is invalid.

### *exception* InvalidTaskBackend

Raised when the requested [`BaseTaskBackend`](#django.tasks.backends.base.BaseTaskBackend) is invalid.

### *exception* TaskResultDoesNotExist

Raised by [`get_result()`](#django.tasks.backends.base.BaseTaskBackend.get_result)
when the provided `result_id` does not exist.

### *exception* TaskResultMismatch

Raised by [`get_result()`](#django.tasks.Task.get_result) when the provided
`result_id` is for a different Task than the current Task.

### Footnotes

* <a id='fnimmediateresult'>**[1]**</a> The [`ImmediateBackend`](#django.tasks.backends.immediate.ImmediateBackend) doesn’t officially support `get_result()`, despite implementing the API, since the result cannot be retrieved from a different thread.
* <a id='fndummypriority'>**[2]**</a> The [`DummyBackend`](#django.tasks.backends.dummy.DummyBackend) has `supports_priority=True` so that it can be used as a drop-in replacement in tests. Since this backend never executes Tasks, the `priority` value has no effect.
* <a id='fnimmediatepriority'>**[3]**</a> The [`ImmediateBackend`](#django.tasks.backends.immediate.ImmediateBackend) has `supports_priority=True` so that it can be used as a drop-in replacement in tests. Because Tasks run as soon as they are scheduled, the `priority` value has no effect.
