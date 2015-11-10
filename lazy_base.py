#!/usr/bin/python
"""Base for lazy classes such as LazyDict and LazyList."""

from __future__ import print_function
import collections
import itertools
import operator


class LazyBase(collections.Iterable):
    """Init, getitem and setitem are not defined here but are expected to be
       defined in subclasses."""
    def __init__(self, arg=None):
        pass

    def __getitem__(self, x):
        """self.__getitem__(x) <=> self[x]."""
        pass

    def __setitem__(self, x, val):
        """self.__setitem__(x, val) <=> self[x] = val."""
        pass

    def __iter__(self):
        """Gets iterator over this object: a.__iter__() <=> iter(a)."""
        idx = 0
        # Eventually, this will raise StopIteration.
        while True:
            yield self[idx]
            idx += 1

    @classmethod
    def ensure_indexable(cls, other):
        """This is used mostly to make sure that 'other' can be treated like a
           lazy dict/list."""
        if not hasattr(other, '__getitem__'):
            other = cls(other)
        return other

    # Defining commonly used functions on items to make them work with lazy
    # objects.
    def __abs__(self):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: abs(self[i]))

    def __add__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: self[i] + other[i])

    def __coerce__(self, other):
        other = self.ensure_indexable(other)
        return self, other

    def __div__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: self[i] / other[i])

    def __divmod__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: divmod(self[i], other[i]))

    def __eq__(self, other):
        other = self.ensure_indexable(other)
        return all(iter(self.__class__(lambda x, i: self[i] == other[i])))

    def __float__(self):
        return self.__class__(lambda x, i: float(self[i]))
  
    def __int__(self):
        return self.__class__(lambda x, i: int(self[i]))

    def __long__(self):
        return self.__class__(lambda x, i: long(self[i]))

    def __float__(self):
        return self.__class__(lambda x, i: float(self[i]))
  
    def __mod__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: self[i] % other[i])

    def __mul__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: self[i] * other[i])

    def __neg__(self):
        return self.__class__(lambda x, i: -self[i])
  
    def __pos__(self):
        return self

    def __pow__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: pow(self[i], other[i]))

    def __radd__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: other[i] + self[i])

    def __rdiv__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: other[i] / self[i])

    def __rdivmod__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: divmod(other[i], self[i]))

    def __rfloordiv__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: other[i] // self[i])

    def __rmod__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: other[i] % self[i])

    def __rmul__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: other[i] * self[i])

    def __rpow__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: pow(other[i], self[i]))

    def __rsub__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: other[i] - self[i])

    def __rtruediv__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: other[i] / self[i])

    def __sub__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: self[i] - other[i])

    def __truediv__(self, other):
        other = self.ensure_indexable(other)
        return self.__class__(lambda x, i: self[i] / other[i])

    def __trunc__(self):
        return self.__class__(lambda x, i: self[i].__trunc__())
