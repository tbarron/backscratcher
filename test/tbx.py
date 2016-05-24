import random
import time
import os

def randomize(ref=None, direction=None, window=None):
    """
    Return a random value based on *ref* (*direction*) randint(*window*).

    *direction* should be +1, -1, or 0 to indicate whether the random value
    should be above, below, or centered on *ref*.
    """
    ref = int(ref + 0.5) or 0
    direction = int(direction) or 0
    window = int(window) or 100
    if 0 < direction:
        high = ref + window
        low = ref
    elif direction < 0:
        high = ref
        low = ref - window
    else:
        high = ref + window/2
        low = ref - window/2
    return random.randint(low, high)
