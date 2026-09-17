from collections.abc import Callable

import pandas as pd

from checkyourdata.schema import CheckConfig, CheckType

# A check implementation takes the full dataset and the check's config,
# and returns (passed, details). Registering a new CheckType means adding
# one function here and one entry in this dict.
CheckImplementation = Callable[[pd.DataFrame, CheckConfig], tuple[bool, dict]]

_REGISTRY: dict[CheckType, CheckImplementation] = {}


def register(check_type: CheckType) -> Callable[[CheckImplementation], CheckImplementation]:
    def decorator(fn: CheckImplementation) -> CheckImplementation:
        _REGISTRY[check_type] = fn
        return fn

    return decorator


def get_implementation(check_type: CheckType) -> CheckImplementation:
    try:
        return _REGISTRY[check_type]
    except KeyError:
        raise NotImplementedError(f"No implementation registered for check_type '{check_type}'") from None


def registered_check_types() -> set[CheckType]:
    return set(_REGISTRY.keys())
