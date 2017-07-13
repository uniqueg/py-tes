from __future__ import print_function

import attr
import simplejson as json

from attr import attrs, attrib
from attr.validators import instance_of, optional, in_


@attrs
class _ListOfValidator(object):
    type = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not all([isinstance(n, self.type) for n in value]):
            raise TypeError(
                "'{name}' must be a list of {type!r} (got {value!r} that is a "
                "list of {actual!r})."
                .format(name=attr.name,
                        type=self.type,
                        actual=value[0].__class__,
                        value=value),
                attr, self.type, value,
            )

    def __repr__(self):
        return (
            "<instance_of validator for type {type!r}>"
            .format(type=self.type)
        )


def list_of(type):
    return _ListOfValidator(type)


def _drop_none(obj):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(_drop_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)(
            (_drop_none(k), _drop_none(v))
            for k, v in obj.items() if k is not None and v is not None
        )
    else:
        return obj


@attrs
class Base(object):

    def as_dict(self, drop_empty=True):
        obj = attr.asdict(self)
        if drop_empty:
                return _drop_none(obj)
        return obj

    def as_json(self, drop_empty=True, sort_keys=True, indent=None):
        return json.dumps(
            self.as_dict(drop_empty),
            sort_keys=sort_keys,
            indent=indent
        )


@attrs
class TaskParameter(Base):
    name = attrib(default=None, validator=optional(instance_of(str)))
    description = attrib(default=None, validator=optional(instance_of(str)))
    url = attrib(validator=instance_of(str))
    path = attrib(validator=instance_of(str))
    type = attrib(validator=in_(["FILE", "DIRECTORY"]))
    contents = attrib(default=None, validator=optional(instance_of(str)))


@attrs
class Resources(Base):
    cpu_cores = attrib(default=None, validator=optional(instance_of(int)))
    ram_gb = attrib(
        default=None, validator=optional(instance_of((float, int)))
    )
    size_gb = attrib(
        default=None, validator=optional(instance_of((float, int)))
    )
    preemptible = attrib(default=None, validator=optional(instance_of(bool)))
    zones = attrib(default=None, validator=optional(list_of(str)))


@attrs
class Ports(Base):
    host = attrib(validator=instance_of(int))
    container = attrib(validator=instance_of(int))


@attrs
class Executor(Base):
    image_name = attrib(validator=instance_of(str))
    cmd = attrib(validator=list_of(str))
    work_dir = attrib(default=None, validator=optional(instance_of(str)))
    stdin = attrib(default=None, validator=optional(instance_of(str)))
    stdout = attrib(default=None, validator=optional(instance_of(str)))
    stderr = attrib(default=None, validator=optional(instance_of(str)))
    ports = attrib(default=None, validator=optional(list_of(Ports)))
    environ = attrib(default=None, validator=optional(instance_of(dict)))


@attrs
class ExecutorLog(Base):
    start_time = attrib(default=None, validator=optional(instance_of(str)))
    end_time = attrib(default=None, validator=optional(instance_of(str)))
    stdout = attrib(default=None, validator=optional(instance_of(str)))
    stderr = attrib(default=None, validator=optional(instance_of(str)))
    exit_code = attrib(default=None, validator=optional(instance_of(int)))
    host_ip = attrib(default=None, validator=optional(instance_of(str)))
    ports = attrib(default=None, validator=optional(list_of(Ports)))


@attrs
class OutputFileLog(Base):
    url = attrib(validator=instance_of(str))
    path = attrib(validator=instance_of(str))
    size_bytes = attrib(validator=instance_of(int))


@attrs
class TaskLog(Base):
    start_time = attrib(default=None, validator=optional(instance_of(str)))
    end_time = attrib(default=None, validator=optional(instance_of(str)))
    metadata = attrib(default=None, validator=optional(instance_of(dict)))
    logs = attrib(default=None, validator=optional(list_of(ExecutorLog)))
    outputs = attrib(default=None, validator=optional(list_of(OutputFileLog)))


@attrs
class Task(Base):
    id = attrib(default=None, validator=optional(instance_of(str)))
    state = attrib(default=None, validator=optional(in_(
        ["UKNOWN", "QUEUED", "INITIALIZING", "RUNNING", "COMPLETE",
         "PAUSED", "CANCELED", "ERROR", "SYSTEM_ERROR"]
    )))
    name = attrib(default=None, validator=optional(instance_of(str)))
    project = attrib(default=None, validator=optional(instance_of(str)))
    description = attrib(default=None, validator=optional(instance_of(str)))
    inputs = attrib(default=None, validator=optional(list_of(TaskParameter)))
    outputs = attrib(default=None, validator=optional(list_of(TaskParameter)))
    resources = attrib(
        default=None, validator=optional(instance_of(Resources))
    )
    executors = attrib(default=None, validator=optional(list_of(Executor)))
    volumes = attrib(default=None, validator=optional(list_of(str)))
    tags = attrib(default=None, validator=optional(instance_of(dict)))
    logs = attrib(default=None, validator=optional(list_of(TaskLog)))


@attrs
class GetTaskRequest(Base):
    id = attrib(validator=instance_of(str))
    view = attrib(
        default=None, validator=optional(in_(["MINIMAL", "BASIC", "FULL"]))
    )


@attrs
class CreateTaskResponse(Base):
    id = attrib(validator=instance_of(str))


@attrs
class ServiceInfoRequest(Base):
    pass


@attrs
class ServiceInfo(Base):
    name = attrib(default=None, validator=optional(instance_of(str)))
    doc = attrib(default=None, validator=optional(instance_of(str)))
    storage = attrib(default=None, validator=optional(list_of(str)))


@attrs
class CancelTaskRequest(Base):
    id = attrib(validator=instance_of(str))


@attrs
class CancelTaskResponse(Base):
    pass


@attrs
class ListTasksRequest(Base):
    project = attrib(default=None, validator=optional(instance_of(str)))
    name_prefix = attrib(default=None, validator=optional(instance_of(str)))
    page_size = attrib(default=None, validator=optional(instance_of(int)))
    page_token = attrib(default=None, validator=optional(instance_of(str)))
    view = attrib(
        default=None, validator=optional(in_(["MINIMAL", "BASIC", "FULL"]))
    )


@attrs
class ListTasksResponse(Base):
    tasks = attrib(validator=list_of(Task))
    next_page_token = attrib(
        default=None, validator=optional(instance_of(str))
    )