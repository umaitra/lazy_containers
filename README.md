Lazily evaluated dicts and lists for python.


Examples of lazy lists:

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



Examples of lazy dicts:


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
