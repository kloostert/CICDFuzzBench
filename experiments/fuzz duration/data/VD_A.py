import itertools as it

from bisect import bisect_left
from typing import List

import numpy as np
import pandas as pd
import scipy.stats as ss

from pandas import Categorical


def VD_A(treatment: List[float], control: List[float]):
    """
    Computes Vargha and Delaney A index
    A. Vargha and H. D. Delaney.
    A critique and improvement of the CL common language
    effect size statistics of McGraw and Wong.
    Journal of Educational and Behavioral Statistics, 25(2):101-132, 2000

    The formula to compute A has been transformed to minimize accuracy errors
    See: http://mtorchiano.wordpress.com/2014/05/19/effect-size-of-r-precision/

    :param treatment: a numeric list
    :param control: another numeric list

    :returns the value estimate and the magnitude
    """
    m = len(treatment)
    n = len(control)

    if m != n:
        raise ValueError("Data d and f must have the same length")

    r = ss.rankdata(treatment + control)
    r1 = sum(r[0:m])

    # Compute the measure
    # A = (r1/m - (m+1)/2)/n # formula (14) in Vargha and Delaney, 2000
    A = (2 * r1 - m * (m + 1)) / (
        2 * n * m
    )  # equivalent formula to avoid accuracy errors

    levels = [0.147, 0.33, 0.474]  # effect sizes from Hess and Kromrey, 2004
    magnitude = ["negligible", "small", "medium", "large"]
    scaled_A = (A - 0.5) * 2

    magnitude = magnitude[bisect_left(levels, abs(scaled_A))]
    estimate = A

    return estimate, magnitude


if __name__ == "__main__":
    # Examples

    # negligible
    F = [
        0.8236111111111111,
        0.7966666666666666,
        0.923611111111111,
        0.8197222222222222,
        0.7108333333333333,
    ]
    G = [
        0.8052777777777779,
        0.8172222222222221,
        0.8322222222222223,
        0.783611111111111,
        0.8141666666666666,
    ]
    print(VD_A(G, F))

    # small
    A = [
        0.478515625,
        0.4638671875,
        0.4638671875,
        0.4697265625,
        0.4638671875,
        0.474609375,
        0.4814453125,
        0.4814453125,
        0.4697265625,
        0.4814453125,
        0.474609375,
        0.4833984375,
        0.484375,
        0.44921875,
        0.474609375,
        0.484375,
        0.4814453125,
        0.4638671875,
        0.484375,
        0.478515625,
        0.478515625,
        0.45703125,
        0.484375,
        0.419921875,
        0.4833984375,
        0.478515625,
        0.4697265625,
        0.484375,
        0.478515625,
        0.4638671875,
    ]
    B = [
        0.4814453125,
        0.478515625,
        0.44921875,
        0.4814453125,
        0.4638671875,
        0.478515625,
        0.474609375,
        0.4638671875,
        0.474609375,
        0.44921875,
        0.474609375,
        0.478515625,
        0.478515625,
        0.474609375,
        0.4697265625,
        0.474609375,
        0.45703125,
        0.4697265625,
        0.478515625,
        0.4697265625,
        0.4697265625,
        0.484375,
        0.45703125,
        0.474609375,
        0.474609375,
        0.4638671875,
        0.45703125,
        0.474609375,
        0.4638671875,
        0.4306640625,
    ]

    print(VD_A(A, B))

    # medium
    C = [
        0.9108333333333334,
        0.8755555555555556,
        0.900277777777778,
        0.9274999999999999,
        0.8777777777777779,
    ]
    E = [
        0.8663888888888888,
        0.8802777777777777,
        0.7816666666666667,
        0.8377777777777776,
        0.9305555555555556,
    ]
    print(VD_A(C, E))

    # Large
    D = [
        0.7202777777777778,
        0.77,
        0.8544444444444445,
        0.7947222222222222,
        0.7577777777777778,
    ]
    print(VD_A(C, D))
