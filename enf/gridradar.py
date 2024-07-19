"""
Module for querying historical frequency data from the GridRadar API.

"""

import os
import time
import logging
from datetime import datetime, timedelta, date

import requests

logger = logging.getLogger(__name__)

GRIDRADAR_API_URL = 'https://api.gridradar.net'
nominal_freq = 50


def query_dates(dates: list[date]) -> list[tuple[str, float]]:
    """
    Queries frequency data for a list of dates.

    Parameters:
    dates (list[date]): List of date objects to query data for.

    Returns:
    list[tuple[str, float]]: List of tuples containing the timestamp and frequency.
    """
    logger.info(f'Querying GridRadar data for {len(dates)} dates')
    collected_data = []
    for d in dates:
        from_ts = datetime.combine(d, datetime.min.time())
        to_ts = from_ts + timedelta(seconds=86399)

        collected_data.extend(query_range(from_ts, to_ts))

    return collected_data


def query_range(from_dt: datetime, to_dt: datetime) -> list[tuple[str, float]]:
    """
    Queries frequency data for a specific time range.

    Parameters:
    from_ts (datetime): Start datetime of the query range.
    to_ts (datetime): End datetime of the query range.

    Returns:
    list[tuple[str, float]]: List of tuples containing the timestamp and frequency.
    """
    logger.info(f'Querying GridRadar data from {from_dt} to {to_dt}')

    account_info = get_account_info()
    logger.info(f'Account info: {account_info}')

    max_span = timedelta(milliseconds=account_info['rq_max_period_historic-median-1s'])
    min_interval = timedelta(milliseconds=account_info['rq_min_interval_historic-median-1s'])

    current_start = from_dt
    collected_data = []

    while current_start < to_dt:
        current_end = min(current_start + max_span, to_dt)

        params = {
            'metric': 'historic-median-1s',
            'area': 'CE',
            'from': to_rfc3339(current_start),
            'to': to_rfc3339(current_end),
            'format': 'json'
        }

        res = auth_get('query', params=params)[0]['datapoints']

        collected_data.extend(res)

        current_start = current_end

        if current_start < to_dt:
            time.sleep(min_interval.total_seconds())

    return [(datetime.fromisoformat(r[1]).isoformat(), r[0]) for r in collected_data]


def get_account_info() -> dict:
    account_info = auth_get('attrib')

    return dict(zip(account_info['columns'], account_info['data'][0]))


def auth_get(endpoint: str, params: dict = None) -> dict:
    """
    Sends an authenticated GET request to the GridRadar API.

    Parameters:
    endpoint (str): The API endpoint to query.
    params (dict): Optional dictionary of query parameters.

    Returns:
    dict: The JSON response from the API.
    """
    logger.info(f'Querying GridRadar API endpoint: {endpoint}')
    api_token = os.environ['GRIDRADAR_API_TOKEN']

    res = requests.get(
        f'{GRIDRADAR_API_URL}/{endpoint}',
        headers={'Authorization': f'Bearer {api_token}'},
        params=params or {}
    )
    res.raise_for_status()

    return res.json()


def to_rfc3339(dt: datetime) -> str:
    """
    Convert a datetime object to RFC 3339 format.

    Parameters:
    dt (datetime): The datetime object.

    Returns:
    str: The RFC 3339 formatted string.
    """
    return dt.replace(microsecond=0).isoformat() + 'Z'


def from_rfc3339(s: str) -> datetime:
    """
    Convert a RFC 3339 formatted string to a datetime object.

    Parameters:
    s (str): The RFC 3339 formatted string.

    Returns:
    datetime: The datetime object.
    """
    return datetime.fromisoformat(s[:-1])
