from typing import Callable, TypeVar


R = TypeVar('R')  # save return type hint
Decoratable = Callable[..., R]


class classproperty:
    def __init__(self, func: Decoratable):
        self.func = func

    def __get__(self, instance, cls):
        return self.func(cls)
