# ENF Analysis Package

## Overview

This package provides a suite of tools for Electric Network Frequency (ENF) analysis, including signal processing, 
similarity matching, and data fetching from the National Grid ESO's system frequency data. The package is organized 
into three main modules:

1. **ENF Matching**: Functions for similarity matching between time series data using various techniques.
2. **Signal Processing**: Functions for processing and analyzing time series data.
3. **Data Fetcher**: Functions for fetching and caching ENF data from external sources.

## Installation

To install the package, clone the repository and install the required dependencies:

```bash
git clone https://github.com/ricdodds/enf.git
cd enf
pip install .
```

## Modules

### 1. ENF Matching

This module provides functions for time series similarity matching using different techniques such as Pearson 
correlation, STUMP and Euclidean distance.

#### Functions

- **`pmcc(Q, T)`**: Perform Pearson correlation between query `Q` and time series `T`.
- **`stump(Q, T)`**: Perform STUMP (Matrix Profile) based similarity search between query `Q` and time series `T`.
- **`euclidean(Q, T)`**: Perform Euclidean distance based similarity search between query `Q` and time series `T`.

### 2. Signal Processing

This module provides functions for processing and analyzing time series data, focusing on techniques like resampling, 
decimation, filtering, and the extraction of the Electric Network Frequency (ENF) series.

#### Functions

- **`enf_series(data, low_cut, high_cut, fs, new_fs=None)`**: Extract the Electric Network Frequency (ENF) series from the input data.
- **`resample(data, fs, new_fs=300)`**: Resample the input data to a new sampling frequency.
- **`decimate_and_interpolate(data, fs, new_fs=300)`**: Decimate and then interpolate the input data to a new sampling frequency.
- **`almost_decimate(data, fs, new_fs=300)`**: Decimate the input data without exact matching of the new sampling frequency.
- **`butter_bandpass_filter(data, order, low_cut, high_cut, fs)`**: Apply a Butterworth bandpass filter to the input data.
- **`stft(data, fs, window_size=64)`**: Perform Short-Time Fourier Transform (STFT) on the input data.
- **`interpolate(zxx, bin_size)`**: Interpolate the STFT results to find the maximum frequency components.
- **`median_filter(f, t, zxx)`**: Apply a median filter to the frequency components of the STFT results.

### 3. Data Fetcher

This module provides functions for fetching and caching Electric Network Frequency (ENF) data from the National Grid ESO's system frequency data.

#### Functions

- **`frequency_data(year, month)`**: Fetch reference ENF data from Great Britain for the given date and cache the response locally.
- **`get_resource(year, month)`**: Get the resource metadata for the given year and month.
- **`get_resources()`**: Get all available resources from the ESO data.

## Usage

### ENF Matching Example

```python
import numpy as np
from enf import match

Q = np.array([...])  # Query time series
T = np.array([...])  # Target time series

# Pearson correlation
results_pmcc = match.pmcc(Q, T)

# STUMP
results_stump = match.stump(Q, T)

# Euclidean distance
results_euclidean = match(Q, T)

```

### Signal Processing Example

```python
import numpy as np
from enf import signal_processing

data = np.array([...])  # Input time series data
low_cut = 49.0
high_cut = 51.0
fs = 1000
new_fs = 300

# Extract ENF series
enf_data = signal_processing.enf_series(data, low_cut, high_cut, fs, new_fs)
```

### Data Fetcher Example

```python
from enf import eso

year = 2023
month = 5

# Fetch frequency data
times, enf = eso.frequency_data(year, month)
```

## License

This package is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Contact

For questions or issues, please open an issue on GitHub or contact the maintainers.
