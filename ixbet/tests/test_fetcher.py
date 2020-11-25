from unittest.mock import Mock

import pytest

import ixbet
from ixbet.fetcher import requests, fetch_json, get_full_url, fetch_top_matches, fetch_match_coefs


def test_fetch_ok(monkeypatch):
    response = {'status': 'ok'}
    monkeypatch.setattr(requests, 'get', lambda _: Mock(json=lambda: response))
    fetched, fetched_url = fetch_json('some_url')
    assert fetched, fetched_url == response


def test_fetch_fail(monkeypatch, caplog):
    exc_txt = 'Fail!'
    url = 'some_url'
    monkeypatch.setattr(requests, 'get', Mock(side_effect=requests.exceptions.RequestException(exc_txt)))
    fetched, fetched_url = fetch_json(url)
    assert fetched == {}
    assert caplog.json[0] == dict(action='fetch', url=url, message='Fail!')


@pytest.mark.parametrize('local_url, url_params, expected_url', [
    pytest.param('/LiveFeed/Get1x2_VZip', dict(sports=1, count=5, lng='en', partner=25, getEmpty='true'),
                 'https://ua-1x-bet.com/LiveFeed/Get1x2_VZip?sports=1&count=5&lng=en&partner=25&getEmpty=true'),
    pytest.param('/LiveFeed/GetGameZip', dict(id=1, lng='en', cfview=0, isSubGames='true', GroupEvents='true',
                                              allEventsGroupSubGames='true', countevents=1, partner=25, marketType=1),
                 'https://ua-1x-bet.com/LiveFeed/GetGameZip?id=1&lng=en&cfview=0&isSubGames=true&GroupEvents=true'
                 '&allEventsGroupSubGames=true&countevents=1&partner=25&marketType=1'),
])
def test_get_full_url(local_url: str, url_params: dict, expected_url: str):
    assert expected_url == get_full_url(local_url, **url_params)


def test_fetch_top_matches(monkeypatch, top_matches):
    monkeypatch.setattr(ixbet.fetcher, 'fetch_json', lambda _url, **_params: (top_matches, _url))
    fetched, url = fetch_top_matches()
    assert url == '/LiveFeed/Get1x2_VZip'
    assert fetched['Success'] is True
    assert len(fetched['Value']) == 5


def test_fetch_match_coefs(monkeypatch, coefs):
    monkeypatch.setattr(ixbet.fetcher, 'fetch_json', lambda _url, **_params: (coefs, _url))
    fetched, url = fetch_match_coefs(1)
    assert url == '/LiveFeed/GetGameZip'
    assert fetched['Success'] is True
    assert len(fetched['Value']['GE'][0]['E']) == 3  # 1 X 2
