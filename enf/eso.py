"""
This module provides functions for fetching and caching Electric Network Frequency (ENF) data from the National Grid
ESO's system frequency data. It utilizes local caching to avoid redundant network requests.

Dependencies:
- os
- requests
- pandas
- joblib
"""

import os

import requests
import pandas as pd
from joblib import Memory

memory = Memory('./cache/eso', verbose=0)

ESO_DATA_URL = 'https://data.nationalgrideso.com/system/system-frequency-data/datapackage.json'
nominal_freq = 50


@memory.cache
def frequency_data(year: int, month: int) -> tuple:
    """
    Fetches reference ENF data from Great Britain for the given date and caches the response locally.

    Parameters:
    year (int): The year of the data to fetch.
    month (int): The month of the data to fetch.

    Returns:
    tuple: A tuple containing numpy arrays of datetime objects and frequency values.
    """
    resource_path = get_resource(year, month)['path']
    df = pd.read_csv(resource_path)

    df['dtm'] = pd.to_datetime(df['dtm'])
    df['f'] = df['f'].astype(float)

    eso_times = df['dtm'].to_numpy()
    eso_enf = df['f'].to_numpy()

    return eso_times, eso_enf


def get_resource(year: int, month: int) -> dict:
    """
    Get the resource metadata for the given year and month.

    Parameters:
    year (int): The year of the resource.
    month (int): The month of the resource.

    Returns:
    dict: The resource metadata.

    Raises:
    KeyError: If the resource for the specified year and month is not found.
    """
    res = requests.get(ESO_DATA_URL)
    res.raise_for_status()

    resources = res.json()['result']['resources']

    try:
        return next(r for r in resources if r['path'].endswith(f"{year}-{month}.csv"))
    except StopIteration:
        raise KeyError(f"Resource for {year}-{month} not found")


def get_resources() -> dict:
    """
    Get all available resources from the ESO data.

    Returns:
    dict: A dictionary with (year, month) tuples as keys and resource paths as values.
    """
    res = requests.get(ESO_DATA_URL)
    res.raise_for_status()

    resources = res.json()['result']['resources']

    monthly_data = {}
    for r in resources:
        year, month = os.path.splitext(r['path'].split('/')[-1])[0].split('-')[1:3]
        month = month.rstrip('_')
        monthly_data[(year, month)] = r['path']

    return monthly_data
