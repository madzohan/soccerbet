import logging
import os
import re
import sys
import time

from ixbet.fetcher import fetch_top_matches, fetch_match_coefs
from ixbet.parser import parse_top_matches, parse_match_coefs
from odds_controller.scheduler import odds_scheduler

# TODO configure logging properly
logging.basicConfig(level=logging.DEBUG if os.getenv('DEBUG', 'false').lower() == 'true' else logging.INFO)
logger = logging.getLogger(__name__)


def is_matching_query(o1: str, o2: str, query: str):
    is_matching = False
    for q in re.split('[- ]', o1) + (re.split('[- ]', o2)):
        if q.lower().startswith(query):
            is_matching = True
            break
    return is_matching


def start_ixbet_top_matches_livefeed(query: str):
    logger.debug(dict(action='job_start', name='ixbet_livefeed_top_matches'))
    fetched_matches, _ = fetch_top_matches()
    if not fetched_matches:
        return
    for match in parse_top_matches(fetched_matches):
        if is_matching_query(match['o1'], match['o2'], query):
            odds_scheduler.add_job(get_ixbet_match_coefs, id='get_ixbet_match_coefs',
                                   kwargs=match, trigger='interval', seconds=5)
            break


def get_ixbet_match_coefs(**match):
    logger.debug(dict(action='job_start', time=time.time(), name='get_ixbet_match_coefs', match_id=match['id']))
    fetched_coefs, _ = fetch_match_coefs(match['id'])
    if not fetched_coefs:
        odds_scheduler.remove_job(job_id='get_ixbet_match_coefs')
        return
    coefs = parse_match_coefs(fetched_coefs)

    # TODO arithmetical mean of ixbet and parimatch coefs
    logging.info(dict(action='job_finish', time=time.time(), name='get_ixbet_match_coefs',
                      message=f'{match["o1"]} vs {match["o2"]} | {coefs["s1"]} : {coefs["s2"]} |'
                              f' x{coefs["o1"]} | x{coefs["x"]} | x{coefs["o2"]} |'))


def parimatch_livefeed():
    # TODO Selenium based parimatch crawler - parse opened page every 5sec
    pass


if __name__ == '__main__':
    start_ixbet_top_matches_livefeed(input('Please enter FC suffix: '))
    try:
        if not odds_scheduler.get_jobs():
            sys.exit(1)
        odds_scheduler.start()
        while True:
            time.sleep(60)  # sometimes 1xbet responds with awful latency
            if not odds_scheduler.get_jobs():
                break
    except (KeyboardInterrupt, SystemExit):
        if odds_scheduler.running:
            odds_scheduler.shutdown()
