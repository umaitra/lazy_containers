#!/usr/bin/python
"""Lazily initialized lists."""

from __future__ import print_function
import collections
import itertools
import operator
import lazy_base
import slice_utils


class LazyList(lazy_base.LazyBase):
    def get_getter_and_len(self, arg=None):
        """Interprets arg as required to turn it into a function that takes
           vals, idx and returns a value. Note that vals itself is an
           argument, so the list can be recursively defined. If a 'length'
           can naturally be defined for the function, this also sets that.
           Note that len_ is a lambda. This is to avoid computing len(arg)
           needlessly when it may lead to an infinite loop."""
        nextgetter = lambda vals, idx: None
        len_ = lambda: None
        if arg is None:
            nextgetter = lambda vals, idx: None
        elif isinstance(arg, collections.Callable):
            nextgetter = arg
        elif hasattr(arg, '__getitem__'):
            nextgetter = lambda vals, idx: arg[idx]
            if hasattr(arg, '__len__'):
                len_ = lambda: len(arg)
        elif isinstance(arg, collections.Iterable):
            nextgetter = lambda vals, idx: arg.next()
            if hasattr(arg, '__len__'):
                len_ = lambda: len(arg)
        else:
            nextgetter = lambda vals, idx: arg
        return nextgetter, len_

    def __init__(self, arg=None):
        """A LazyList can be initialized with:
            - A function that takes vals, idx as arguments to tell what
              vals[idx] should be. The value of vals[idx] can depend on
              smaller indices in vals but should not depend on larger ones.
            - An indexable object x for which x[idx] makes sense.
            - An iterable x for which x.next() makes sense.
            - A constant.

          If no argument is provided, this defaults to an infinite list of
          Nones."""
        # A LazyList object has three attributes:
        # - arr: Already computed values.
        # - nextgetters: Functions which set how particular slices are
        #    computed. Multiple nextgetters mean that latter ones have
        #    priority. Others are still computed in case they involve
        #    iterators, or if the idx will not be set by latter getters.
        # - len_: This will only be non None if the list has a known upper
        #    bound on length."""
        self.arr = []
        getter, len_ = self.get_getter_and_len(arg)
        self.nextgetters = [(
            slice(0, None, 1), getter, len_)]
        self.len_ = None

    def get_next_with_getter(self, idx, slice_, nextgetter):
        """Returns (next value) if attempt to get next value was successful."""
        slice_idx = slice_utils.get_idx_in_slice(slice_, idx)
        if slice_idx is None:
            return None, False
        try:
            return nextgetter(self.arr, slice_idx), True
        except Exception as e:
            return None, False

    def get_next(self, idx):
        """Gets self[idx] given that self[x] is set for x <= idx."""
        final_val = None
        found_val = False
        for slice_, nextgetter, _ in self.nextgetters:
            val, status = self.get_next_with_getter(
                idx, slice_, nextgetter)
            if status:
                final_val = val
                found_val = True
        if found_val:
            return final_val
        else:
            self.len_ = idx
            raise StopIteration

    def fill_to(self, idx):
        """Fills vals of self till idx."""
        while idx >= len(self.arr):
            self.arr.append(self.get_next(len(self.arr)))

    def getidx(self, idx):
        """Gets vals[idx] given that idx is a number (not a slice)."""
        # Note that we don't have anything like get_idx. We use fill_to,
        # thus making sure that all prior values are also filled.
        self.fill_to(idx)
        return self.arr[idx]

    def getslice(self, slice_):
        """Gets slice from the list."""
        # Note that the slice can be infinite, so we return another lazy list.
        slice_list = LazyList(slice_utils.generate_slice(slice_))
        return LazyList(lambda vals, idx: self.getidx(slice_list[idx]))

    def __getitem__(self, x):
        """self.__getitem__(x) <=> self[x]."""
        # Just call respective function depending on whether or not x is a
        # slice.
        if isinstance(x, slice):
            return LazyList(self.getslice(x))
        else:
            return self.getidx(x)

    def setidx(self, x, val):
        """Sets a particular index x to val."""
        self.fill_to(x)
        self.arr[x] = val

    def setslice(self, slice_, val):
        """Sets a slice to val."""
        # We basically just update the nextgetters.
        getter, len_ = self.get_getter_and_len(val)
        self.nextgetters.append((slice_, getter, len_))
        # Old value of self.len_ is invalid now.
        self.len_ = None

    def __setitem__(self, x, val):
        """self.__setitem__(x, val) <=> self[x] = val."""
        # Just calls the appropriate function depending on whether or not x
        # is a slice.
        if isinstance(x, slice):
            self.setslice(x, val)
        else:
            self.setidx(x, val)

    def set_len(self):
        """Set self.len_ depending on len_ function of components."""
        min_len = self.len_
        for _, _, len_ in self.nextgetters:
            len_val = len_()
            if len_val is None:
                # We have an infinite component.
                return
            if (min_len is None) or (len_val < min_len):
                min_len = len_val
        self.len_ = min_len

    def actual_len(self):
        """Sets and returns self.len_. Is different from __len__ because
           __len__ is not allowed to return None. On the other hand, the most
           meaningful value of self.len_ will often be None."""
        if self.len_ is None:
            self.set_len()
        return self.len_

    def __len__(self):
        """self.__len__() <=> len(self)."""
        # Just find the actual len and if it is None, return 0 to make python
        # happy. Else return actual len.
        len_ = self.actual_len()
        if len_ is None:
            return 0
        else:
            return len_

    def __str__(self):
        """self.__str__() <=> str(self)."""
        # vals[0], vals[1], vals[2],... <vals[len-1]>
        len_ = self.actual_len()
        str_ = ''
        # If some index is not found, just return whatever else we have found.
        try:
            for idx in range(3):
                str_ += str(self[idx]) + ','
            str_ += '... '
            if len_ is not None:
                str_ += str(self[len_ - 1])
        except StopIteration as e:
            pass
        return str_

    def __repr__(self):
        """Used by eg. the REPL or pprint."""
        return str(self)


def get_peano():
    """Lazy numbers starting from 0."""
    a = LazyList([0])
    a[1:] = a + 1
    return a


def get_fact():
    """Lazy factorials."""
    a = LazyList([1])
    a[1:] = a * get_peano()[1:]
    return a


def get_fib():
    """Lazy fibonacci sequence."""
    a = LazyList([0, 1])
    a[2:] = a[1:] + a
    return a


def main():
    # Numbers.
    p = get_peano()
    assert p[1] == 1
    assert p[15] == 15

    # Factorials.
    f = get_fact()
    assert f[6] == 720
    assert f[3] == 6

    # Fibonacci.
    fib = get_fib()
    assert fib[0] == 0
    assert fib[3] == 2
    assert fib[5] == 5
    assert fib[7] == 13


if __name__ == '__main__':
    main()
