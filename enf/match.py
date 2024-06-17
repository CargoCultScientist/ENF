"""
This module provides several functions for time series similarity matching using different techniques
including Pearson correlation, STUMP and Euclidean distance.

Dependencies:
- stumpy
- numpy
- scipy
"""

import stumpy
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.spatial import distance


def pmcc(Q: np.ndarray, T: np.ndarray) -> list:
    """
    Perform Pearson correlation between query Q and time series T.

    Parameters:
    Q (np.ndarray): The query time series.
    T (np.ndarray): The target time series.

    Returns:
    list: Sorted list of tuples containing the index and correlation coefficient.
    """
    v = sliding_window_view(T, len(Q))

    return sorted(
        [(i, np.corrcoef(w, Q)[0][1]) for i, w in enumerate(v)],
        key=lambda item: -item[1]
    )


def stump(Q: np.ndarray, T: np.ndarray) -> list:
    """
    Perform STUMP (Matrix Profile) based similarity search between query Q and time series T.

    Parameters:
    Q (np.ndarray): The query time series.
    T (np.ndarray): The target time series.

    Returns:
    list: Sorted list of tuples containing the index and distance.
    """
    matches = stumpy.match(
        np.array(Q, dtype=float),
        np.array(T, dtype=float),
        # max_distance=lambda D: max(np.mean(D) - 4 * np.std(D), np.min(D))
    )

    return sorted(
        [(i, d) for d, i in matches],
        key=lambda item: item[1]
    )


def euclidean(Q: np.ndarray, T: np.ndarray) -> list:
    """
    Perform Euclidean distance based similarity search between query Q and time series T.

    Parameters:
    Q (np.ndarray): The query time series.
    T (np.ndarray): The target time series.

    Returns:
    list: Sorted list of tuples containing the index and Euclidean distance.
    """
    v = sliding_window_view(T, len(Q))

    return sorted(
        [(i, distance.euclidean(w, Q)) for i, w in enumerate(v)],
        key=lambda item: item[1]
    )
