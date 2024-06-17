"""
This module provides several functions for processing and analyzing time series data, particularly focusing on
techniques like resampling, decimation, filtering, and the extraction of the Electric Network Frequency (ENF) series.

Dependencies:
- math
- numpy
- scipy
"""

import math
import numpy as np
from scipy import signal


def enf_series(data: np.ndarray, low_cut: float, high_cut: float, fs: int, new_fs: int = None) -> np.ndarray:
    """
    Extract the Electric Network Frequency (ENF) series from the input data.

    Parameters:
    data (np.ndarray): The input time series data.
    low_cut (float): The low cutoff frequency for bandpass filtering.
    high_cut (float): The high cutoff frequency for bandpass filtering.
    fs (int): The sampling frequency of the input data.
    new_fs (int, optional): The new sampling frequency for resampling. Defaults to None.

    Returns:
    np.ndarray: The extracted ENF series.
    """
    if new_fs and new_fs < fs:
        fs, data = resample(data, fs, new_fs)

    filter_order = 4
    data = butter_bandpass_filter(
        data, filter_order, low_cut, high_cut, fs
    )

    f, t, zxx = stft(data, fs)

    # bin_size = f[1] - f[0]
    # return interpolate(zxx, bin_size)

    return median_filter(f, t, zxx)


def resample(data: np.ndarray, fs: int, new_fs: int = 300) -> tuple:
    """
    Resample the input data to a new sampling frequency.

    Parameters:
    data (np.ndarray): The input time series data.
    fs (int): The original sampling frequency.
    new_fs (int, optional): The new sampling frequency. Defaults to 300.

    Returns:
    tuple: The new sampling frequency and the resampled data.
    """
    _validate_fs(fs, new_fs)

    wave_duration = len(data) / fs
    num_samples = int(wave_duration * new_fs)

    return new_fs, signal.resample(data, num_samples)


def decimate_and_interpolate(data: np.ndarray, fs: int, new_fs: int = 300) -> tuple:
    """
    Decimate and then interpolate the input data to a new sampling frequency.

    Parameters:
    data (np.ndarray): The input time series data.
    fs (int): The original sampling frequency.
    new_fs (int, optional): The new sampling frequency. Defaults to 300.

    Returns:
    tuple: The new sampling frequency and the processed data.
    """
    _validate_fs(fs, new_fs)

    gcd = math.gcd(fs, new_fs)

    decimation_factor = fs // gcd
    interpolation_factor = new_fs // gcd

    decimated_data = signal.decimate(data, decimation_factor, ftype='fir')

    final_length = len(decimated_data) * interpolation_factor
    interpolated_data = signal.resample(decimated_data, final_length)

    return new_fs, interpolated_data


def almost_decimate(data: np.ndarray, fs: int, new_fs: int = 300) -> tuple:
    """
    Decimate the input data without exact matching of the new sampling frequency.

    Parameters:
    data (np.ndarray): The input time series data.
    fs (int): The original sampling frequency.
    new_fs (int, optional): The new sampling frequency. Defaults to 300.

    Returns:
    tuple: The new sampling frequency and the decimated data.
    """
    _validate_fs(fs, new_fs)

    decimation_factor = math.floor(fs / new_fs)
    decimated_data = signal.decimate(data, decimation_factor, ftype='fir')

    wave_duration = len(data) / fs
    new_fs = int(len(decimated_data) / wave_duration)

    return new_fs, decimated_data


def _validate_fs(fs: int, new_fs: int) -> None:
    """
    Validate the sampling frequencies.

    Parameters:
    fs (int): The original sampling frequency.
    new_fs (int): The new sampling frequency.

    Raises:
    ValueError: If the new sampling frequency is greater than the original sampling frequency.
    """
    if fs < new_fs:
        raise ValueError("New sample rate must be less than the original sample rate")


def butter_bandpass_filter(data: np.ndarray, order: int, low_cut: float, high_cut: float, fs: int) -> np.ndarray:
    """
    Apply a Butterworth bandpass filter to the input data.

    Parameters:
    data (np.ndarray): The input time series data.
    order (int): The order of the filter.
    low_cut (float): The low cutoff frequency.
    high_cut (float): The high cutoff frequency.
    fs (int): The sampling frequency of the input data.

    Returns:
    np.ndarray: The filtered data.
    """
    sos = butter_bandpass(
        order, low_cut, high_cut, fs
    )

    return signal.sosfilt(sos, data)


def butter_bandpass(order: int, low_cut: float, high_cut: float, fs: int, output: str = 'sos') -> np.ndarray:
    """
    Create a Butterworth bandpass filter.

    Parameters:
    order (int): The order of the filter.
    low_cut (float): The low cutoff frequency.
    high_cut (float): The high cutoff frequency.
    fs (int): The sampling frequency.
    output (str, optional): The output type of the filter coefficients. Defaults to 'sos'.

    Returns:
    np.ndarray: The filter coefficients.
    """
    return signal.butter(
        order,
        [low_cut, high_cut],
        btype='bandpass',
        output=output,
        fs=fs
    )


def stft(data: np.ndarray, fs: int, window_size: int = 64) -> tuple:
    """
    Perform Short-Time Fourier Transform (STFT) on the input data.

    Parameters:
    data (np.ndarray): The input time series data.
    fs (int): The sampling frequency.
    window_size (int, optional): The window size in seconds. Defaults to 64.

    Returns:
    tuple: Frequencies, times, and STFT of the input data.
    """
    window_size_seconds = window_size
    nperseg = fs * window_size_seconds
    noverlap = fs * (window_size_seconds - 1)

    return signal.stft(data, fs, nperseg=nperseg, noverlap=noverlap)


def interpolate(zxx: np.ndarray, bin_size: float) -> list:
    """
    Interpolate the STFT results to find the maximum frequency components.

    Parameters:
    zxx (np.ndarray): The STFT of the input data.
    bin_size (float): The bin size of the frequency components.

    Returns:
    list: The interpolated maximum frequency components.
    """
    def quadratic_interpolation(data: np.ndarray, max_idx: int, bin_size: float) -> float:
        left = data[max_idx - 1]
        center = data[max_idx]
        right = data[max_idx + 1]

        p = 0.5 * (left - right) / (left - 2 * center + right)

        return (max_idx + p) * bin_size

    max_freqs = []
    for spectrum in np.abs(np.transpose(zxx)):
        max_amp = np.amax(spectrum)
        max_freq_idx = np.where(spectrum == max_amp)[0][0]

        max_freq = quadratic_interpolation(spectrum, max_freq_idx, bin_size)
        max_freqs.append(max_freq)

    return max_freqs


def median_filter(f: np.ndarray, t: np.ndarray, zxx: np.ndarray) -> np.ndarray:
    """
    Apply a median filter to the frequency components of the STFT results.

    Parameters:
    f (np.ndarray): The frequency components.
    t (np.ndarray): The time components.
    zxx (np.ndarray): The STFT of the input data.

    Returns:
    np.ndarray: The filtered frequency components.
    """
    peak_freqs = [
        f[idx] for i in range(len(t))
        if (idx := np.argmax(zxx[:, i]))
    ]

    return signal.medfilt(peak_freqs, kernel_size=29)
