import logging
import os
from urllib.parse import urljoin, urlencode, urlparse, parse_qsl, urlunparse

import requests

logger = logging.getLogger(__name__)

SCHEMA = 'https'
DOMAIN = 'ua-1x-bet.com'

IXBET_FETCH_MATCHES_COUNT = os.getenv('IXBET_FETCH_MATCHES_COUNT', 5)


def get_full_url(url: str, **params):
    url_parts = list(urlparse(urljoin(f'{SCHEMA}://{DOMAIN}', url)))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def fetch_json(url: str, **params) -> tuple[dict, str]:
    full_url = ''
    fetched = {}
    try:
        full_url = get_full_url(url, **params)
        response = requests.get(full_url)
        response.raise_for_status()
        fetched = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(dict(action='fetch', url=url, message=str(e)))
    return fetched, full_url


def fetch_top_matches() ->  tuple[dict, str]:
    matches, full_url = fetch_json('/LiveFeed/Get1x2_VZip', sports=1, count=IXBET_FETCH_MATCHES_COUNT,
                                   lng='en', partner=25, getEmpty='true')
    if not matches['Success']:
        logger.error(dict(action='fetch_top_matches', url=full_url, message='URL params misorder'))
        matches = {}
    return matches, full_url


def fetch_match_coefs(match_id: int):
    coefs, full_url = fetch_json('/LiveFeed/GetGameZip',
                                 id=match_id, lng='en', cfview=0, isSubGames='true', GroupEvents='true',
                                 allEventsGroupSubGames='true', countevents=1, partner=25, marketType=1)
    if not coefs['Success']:
        logger.error(dict(action='fetch_match_coefs', match_id=match_id, url=full_url,
                          message='URL params misorder OR no such match id'))
        coefs = {}
    return coefs, full_url
