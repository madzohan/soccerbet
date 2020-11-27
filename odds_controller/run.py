import logging
import os
import sys
import time

from ixbet.fetcher import fetch_top_matches, fetch_match_coefs
from ixbet.parser import parse_top_matches, parse_match_coefs
from odds_controller.scheduler import OddsScheduler

# TODO configure logging properly
from odds_controller.utils import is_matching_query
from parimatch.parser import ParimatchParser

logging.basicConfig(level=logging.DEBUG if os.getenv('DEBUG', 'false').lower() == 'true' else logging.INFO)
logger = logging.getLogger(__name__)


def ixbet_livefeed(query: str, pm_parser: ParimatchParser):
    logger.debug(dict(action='job_start', time=time.time(), name='ixbet_livefeed'))
    fetched_matches, _ = fetch_top_matches()
    if not fetched_matches:
        return
    for match in parse_top_matches(fetched_matches):
        if is_matching_query(match['o1'], match['o2'], query):
            odds_scheduler.add_job(get_pari_match_coefs, id='get_pari_match_coefs',
                                   args=(pm_parser,), kwargs=match, trigger='interval', seconds=5)
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


def get_parimatch_parser() -> ParimatchParser:
    logger.debug(dict(action='job_start', time=time.time(), name='parimatch_livefeed'))
    parser = ParimatchParser()
    logger.debug(dict(action='job_end', time=time.time(), name='parimatch_livefeed'))
    return parser


def get_pari_match_coefs(parser, **match):
    logger.debug(dict(action='job_start', time=time.time(), name='get_pari_match_coefs'))
    if not (parser.match or parser.find_match(match)):
        logger.info(dict(action='job_finish', time=time.time(), name='get_pari_match_coefs', message='no match found'))
        if not parser.is_comparable_request:
            odds_scheduler.remove_job(job_id='get_pari_match_coefs')
        return
    score = parser.get_match_score()
    score_msg = f'{score["s1"]}: {score["s2"]}' if score else 'no score available'
    coefs = parser.get_match_odds()
    coefs_msg = f'x{coefs["o1"]} | x{coefs["x"]} | x{coefs["o2"]}' if coefs else 'no odds available'
    logging.info(dict(action='job_finish', time=time.time(), name='get_pari_match_coefs',
                      message=f'{match["o1"]} vs {match["o2"]} | {score_msg} | {coefs_msg} |'))


if __name__ == '__main__':
    _q = input('Please enter FC suffix: ')
    odds_scheduler = OddsScheduler()
    parimatch_parser = get_parimatch_parser()
    ixbet_livefeed(_q, parimatch_parser)
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
        parimatch_parser.quit()
