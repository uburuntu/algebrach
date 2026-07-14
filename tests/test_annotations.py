import importlib
import inspect

import pytest

MODULE_NAMES = (
    "airtable.kek_storage",
    "common.executor",
    "common.tg",
    "handlers.basic",
    "handlers.kek.kek",
    "handlers.kek.kek_add",
    "handlers.kek.kek_info",
    "handlers.kek.kek_inline",
    "middlewares.event_context",
    "middlewares.log_updates",
    "middlewares.skip_anonymous",
    "middlewares.throttle_users",
)


@pytest.mark.parametrize("module_name", MODULE_NAMES)
def test_runtime_signatures_are_introspectable(module_name):
    module = importlib.import_module(module_name)
    callables = []

    for value in vars(module).values():
        if inspect.isfunction(value) and value.__module__ == module_name:
            callables.append(value)
        elif inspect.isclass(value) and value.__module__ == module_name:
            callables.extend(
                member for member in vars(value).values() if inspect.isfunction(member)
            )

    assert callables
    for callable_ in callables:
        inspect.signature(callable_)
