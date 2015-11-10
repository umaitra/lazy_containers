#!/usr/bin/python
"""General utilities to deal with slices."""

def sign(x):
    """Simple/naive sign function."""
    if x < 0:
        return -1
    if x > 0:
        return 1
    return 0


def defaulted_slice(slice_):
    """Interpret Nones as expected in a slice."""
    start, stop, step = slice_.start, slice_.stop, slice_.step
    if start is None:
        start = 0
    if step is None:
        step = 1
    return slice(start, stop, step)


def generate_slice(slice_):
    """Get a generator to iterate over a slice."""
    slice_ = defaulted_slice(slice_)
    start, stop, step = slice_.start, slice_.stop, slice_.step
    idx = start
    sign_step = sign(step)
    while (stop is None) or ((sign(stop - idx) * sign_step) > 0):
        yield idx
        idx += step
    raise StopIteration


def get_idx_in_slice(slice_, idx):
    """Get the position of an index in a slice."""
    slice_ = defaulted_slice(slice_)
    start, stop, step = slice_.start, slice_.stop, slice_.step
    if idx == start:
        return 0
    # We have already checked idx == start earlier, so now this means we will
    # never reach idx.
    if step == 0:
        return None
    # idx is one direction from start, step is taking us the other way.
    # The equals case can be skipped here as we have already taken care of it
    # above.
    if sign(step) * sign(idx - start) <= 0:
        return None
    num = idx - start
    denom = step
    # The slice will cross idx without touching it.
    if num % denom != 0:
        return None
    return num / denom
