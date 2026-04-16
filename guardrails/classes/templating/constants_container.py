import os
from lxml import etree as ET


class ConstantsContainer:
    def __init__(self):
        self._constants = {}
        self.fill_constants()

    def fill_constants(self) -> None:
        pass

    def __getitem__(self, key):
        return self._constants[key]

    def __setitem__(self, key, value):
        self._constants[key] = value

    def __delitem__(self, key):
        del self._constants[key]

    def __iter__(self):
        return iter(self._constants)

    def __len__(self):
        return len(self._constants)

    def __contains__(self, key):
        return key in self._constants

    def __repr__(self):
        return repr(self._constants)

    def __str__(self):
        return str(self._constants)

    def items(self):
        return self._constants.items()

    def keys(self):
        return self._constants.keys()

    def values(self):
        return self._constants.values()
