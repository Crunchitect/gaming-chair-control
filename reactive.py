import random
from typing import Callable


_callbacks: list[tuple[float, Callable]] = []


class ref:
    def __init__(self, val):
        global _callbacks
        self._value = val
        self._id = random.random()

    def __bool__(self):
        return bool(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value == value:
            return
        for i in _callbacks:
            if i[0] == self._id:
                i[1](self._value, value)
        self._value = value


def watch(ref_obj: ref, func: Callable):
    _callbacks.append((ref_obj._id, func))

