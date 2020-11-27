import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from odds_controller.utils import is_matching_query

WEBDRIVER_CAPABILITIES = {
    "browserName": "chrome",
    "screenResolution": "1280x720",
    "name": "madzohan",
    "selenoid:options": {
        "enableLog": True
    },
    'acceptSslCerts': True,
    'acceptInsecureCerts': True,
    'timeZone': 'Europe/London',
    'goog:chromeOptions': {
        'args': []
    }
}

SELENOID_HOST = os.getenv('SELENOID_HOST', 'localhost')
SELENOID_PORT = os.getenv('SELENOID_PORT', '4444')


class ParimatchParser:
    url = 'https://air2.parimatch.com/en/live?tab=2|F'
    match = None
    o1 = None
    o2 = None
    _match_not_found_threshold = 3

    def __init__(self):
        self.driver = webdriver.Remote(command_executor=f'http://{SELENOID_HOST}:{SELENOID_PORT}/wd/hub',
                                       desired_capabilities=WEBDRIVER_CAPABILITIES)
        self.driver.maximize_window()
        self.open_main_page()
        self.navigate_football_matches()

    @property
    def is_comparable_request(self):
        return self._match_not_found_threshold > 0

    def open_main_page(self):
        self.driver.get(self.url)  # average DOMContentLoaded: 823 ms

    def navigate_football_matches(self):
        self.driver.execute_script("window.scrollTo(0, window.scrollY + 500)")  # focus top matches

    def find_match(self, ixbet_match: dict) -> bool:
        matches = WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//live-block-championship[.//span[@class='championship-name-title__text' and"
                           " not(contains(., 'Cyberfootball'))]]//live-block")))
        for match in matches:
            _ = match.location_once_scrolled_into_view
            teams = match.find_elements_by_xpath(".//div[@class='live-block-competitors__item-name']")
            o1, o2 = [team.text for team in teams]
            for key in ['o1', 'o2']:
                is_matching = is_matching_query(o1, o2, query=ixbet_match[key])
                if is_matching:
                    self.match = match
                    return True
        if self.is_comparable_request:
            self.driver.refresh()
            self._match_not_found_threshold -= 1
        return False  # match not found

    def get_match_odds(self) -> dict:
        odds_nums = self.match.find_elements_by_xpath(
            ".//main-markets[@type='live']//main-markets-group[position()=1]//span[contains(@class, 'outcome__coeff')]")
        try:
            o1, x, o2 = [float(num.text) for num in odds_nums]
            odds = dict(o1=o1, x=x, o2=o2)
        except ValueError:
            odds = {}
        return odds

    def get_match_score(self) -> dict:
        score_nums = self.match.find_elements_by_xpath(
            ".//div[@class='live-score-box-single']/span[position()=1 or position()=last()]")
        try:
            s1, s2 = [int(num.text) for num in score_nums]
            score = dict(s1=s1, s2=s2)
        except ValueError:
            score = {}
        return score

    def quit(self, is_screenshot_needed=False):
        if is_screenshot_needed:
            self.driver.get_screenshot_as_file(self.driver.session_id + '.png')
        self.driver.quit()
