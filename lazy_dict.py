#!/usr/bin/python
"""Lazy dictionary, whose indices are computed as/when required."""

from __future__ import print_function
import collections
import itertools
import operator
import lazy_base
import slice_utils


class LazyDict(lazy_base.LazyBase):
    def __init__(self, x=None):
        """A LazyDict can be initialized with:
            - A function that takes vals, i as arguments and returns what
              vals[i] should be. The value of vals[i] can depend on other
              elements in vals. But try to avoid circular dependencies as that
              is not handled.
            - Any object x that can be indexed like x[i].
            - Any constant value.

           By default it gives None for all values."""
        if x is None:
            # May have made sense to interpret it as an empty dict too.
            self.fn = lambda vals, i: None
        elif isinstance(x, collections.Callable):
            # x is a function here.
            self.fn = x
        elif hasattr(x, '__getitem__'):
            # x is indexable.
            self.fn = lambda vals, i: x[i]
        else:
            # x is the value for all indices of the dict.
            self.fn = lambda vals, i: x
        self.vals = {}

    def getidx(self, idx):
        # Compute self.vals[x] only if needed.
        if idx not in self.vals:
            self.vals[idx] = self.fn(self, idx)
        return self.vals[idx]

    def getslice(self, x):
        # We can take slices of a lazy dict. This is not essential
        # functionality.
        for idx in slice_utils.generate_slice(x):
            yield self.getidx(idx)
        raise StopIteration

    def __getitem__(self, x):
        """self.__getitem__(x) <=> self[x]."""
        # Depending on whether x is a slice or not, call the appropriate
        # function.
        if isinstance(x, slice):
            return self.getslice(x)
        else:
            return self.getidx(x)

    def __setitem__(self, x, val):
        """self.__setitem__(x, val) <=> self[x] = val."""
        # Won't allow setting slices, just like normal dicts.
        self.vals[x] = val


def main():
    # Fibonacci!
    fibs = LazyDict(lambda x, i: 0 if i <= 0 else x[i - 1] + x[i - 2])
    fibs[0] = 0
    fibs[1] = 1
    assert(fibs[12] == 144)
    assert(fibs[13] == 233)
    fibs_l = list(fibs[82:83])
    assert(len(fibs_l)) == 1
    assert(fibs_l[0] == 61305790721611591L)

    # With this you can easily compute the collatz function.
    def collatz_fn(x, i):
        if i <= 1:
            return 0
        if i % 2 == 0:
            return 1 + x[i / 2]
        else:
            return 1 + x[3 * i + 1]
    collatz = LazyDict(collatz_fn)
    assert (collatz[93] == 17)
    assert ((collatz + collatz)[93] == 34)
    assert ((collatz + 3)[93] == 20)

    # Finding gcd using a lazy dict - this one is a bit wasteful.
    def gcd_fn(vals, (x, y)):
        if x > y:
            return vals[(y, x)]
        if x == 0:
            return y
        return vals[(y % x, x)]
    gcd = LazyDict(gcd_fn)
    assert (gcd[(100, 96)] == 4)

    # Find the probability of being at i after 'step' steps in a random walk.
    # This one is good at using old values efficiently.
    def hit_prob_fn(vals, (i, step)):
        if step <= 0:
            if i == 0:
                return 1.0
            else:
                return 0.0
        else:
            return 0.5 * (vals[(i + 1, step - 1)] + vals[(i - 1, step - 1)])
    hit_prob = LazyDict(hit_prob_fn)
    assert (-0.00001 < (hit_prob[(0, 30)] - 0.144464448094) < 0.00001)


if __name__ == '__main__':
    main()
