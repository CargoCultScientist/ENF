"""
This module provides functions for fetching and caching Electric Network Frequency (ENF) data from the National Grid
ESO's system frequency data. It utilizes local caching to avoid redundant network requests.

"""

import os
import logging
from datetime import datetime, date

import requests
import pandas as pd

logger = logging.getLogger(__name__)

ESO_DATA_URL = 'https://data.nationalgrideso.com/system/system-frequency-data/datapackage.json'
nominal_freq = 50


def query_dates(dates: list[date]) -> list[tuple[str, float]]:
    """
    Queries frequency data for a list of dates.

    Parameters:
    dates (list[date]): List of date objects to query data for.

    Returns:
    list[tuple[str, float]]: List of tuples containing the timestamp and frequency.
    """
    logger.info(f'Querying ESO data for {len(dates)} dates')

    collected_data = []

    unique_months = set((d.year, d.month) for d in dates)
    for year, month in unique_months:
        collected_data.extend(
            query_month(year, month)
        )

    return [r for r in collected_data if datetime.fromisoformat(r[0]).date() in dates]


def query_month(year: int, month: int) -> list[tuple[str, float]]:
    """
    Fetches reference ENF data from Great Britain for the given date and caches the response locally.

    Parameters:
    year (int): The year of the data to fetch.
    month (int): The month of the data to fetch.

    Returns:
    tuple: A tuple containing numpy arrays of datetime objects and frequency values.
    """
    logger.info(f'Querying ESO data for {year}-{month}')

    resource_path = get_resource(year, month)['path']
    df = pd.read_csv(resource_path)

    df['dtm'] = pd.to_datetime(df['dtm'])
    df['f'] = df['f'].astype(float)

    return [(dt.isoformat(), f) for dt, f in zip(df['dtm'], df['f'])]


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
