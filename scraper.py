from collections import defaultdict
from typing import NamedTuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
import datetime
import re
import time


class GolfCourse(NamedTuple):
    id: str
    tag: str
    name: str


COURSES = [
    GolfCourse('12203', 'rancho-park-golf-course', 'Rancho Park Golf Course'),
]

PLAYER_COUNT = 2
MESSAGE_OUTPUT_FILE = "message.txt"


class GolfNowScraper():
    URL_TEMPLATE = (
        "https://www.golfnow.com/tee-times/facility/{course_id}-{course_tag}/search" + 
        "#sortby=Date&view=Grouping&holes=3&timeperiod={end_hour}&timemax=30&timemin=10&players={player_count}" + 
        "&pricemax=10000&pricemin=0&promotedcampaignsonly=false")
    END_HOUR_9PM = 42
    END_HOUR_3PM = 30

    def __init__(self, debug_mode=False, filter_times=False) -> None:
        self.debug_mode = debug_mode
        self.filter_times = filter_times
        chrome_options = Options()
        if not debug_mode:
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=chrome_options)

    def scrape(self, target_course: GolfCourse, target_date: datetime.date, player_count: int) -> list[str]:
        self._load_landing_page(target_course=target_course, player_count=player_count)
        self._filter_date(target_date=target_date)
        self._filter_course(target_course=target_course)
        self._filter_player_count(player_count=player_count)
        # self._validate_results(target_course=target_course, target_date=target_date)
        # self._select_list_view()
        results = self._parse_results()
        self._snapshot_results(target_course=target_course, target_date=target_date, results=str(results))
        return results

    def close(self):
        self.browser.close()

    def _load_landing_page(self, target_course: GolfCourse, player_count: int) -> None:
        url = self.URL_TEMPLATE.format(course_id=target_course.id, 
                                       course_tag=target_course.tag,
                                       end_hour=self.END_HOUR_3PM if self.filter_times else self.END_HOUR_9PM,
                                       player_count=PLAYER_COUNT)       
        self.browser.get(url)
        self.browser.maximize_window()
        self._pause()

    # # TODO(vifong): TURN ON FILTERING TIMES
    # def _filter_time(self) -> None:
    #     # pass

    def _filter_player_count(self, player_count: int) -> None:
        golfers_btn = self.browser.find_element(By.XPATH, "//a[@title='Golfers']")
        golfers_btn.click()
        self._pause()

        two_golfers_radio_input = self.browser.find_element(
            By.XPATH, "//input[@type='radio' and @value='{players}']".format(players=player_count))
        parent_element = two_golfers_radio_input.find_element(By.XPATH, "..")
        parent_element.click()
        self._pause()

    def _filter_date(self, target_date: datetime.date) -> None:
        date_btn = self.browser.find_element(By.ID, "fed-search-big-date")
        date_btn.click()
        self._pause()

        picker_month = self.browser.find_element(By.CLASS_NAME, "picker__month")
        picker_year = self.browser.find_element(By.CLASS_NAME, "picker__year")
        picker_nav_next = self.browser.find_element(By.CLASS_NAME, "picker__nav--next")

        # Check the month
        month = '{0:%b}'.format(target_date)
        print("target_month:", month)
        print("picker_month:", picker_month.text)
        while picker_month.text != month:
            print("\ttarget_month: ", month)
            print("\tpicker_month: ", picker_month.text)
            picker_nav_next.click()

        # Check the year
        print("target_year:", target_date.year)
        print("picker_year:", picker_year.text)
        if picker_year.text != str(target_date.year):
            print("TODO: error")

        # Select the day
        picker_day = self.browser.find_element(By.XPATH, "//div[@aria-label='{date}']".format(date=target_date.strftime("%a, %b %d")))
        print("target_day:", target_date.day)
        print("picker_day:", picker_day.text)
        picker_day.click()
        self._pause()

    def _filter_course(self, target_course: GolfCourse) -> None:
        search_bar = self.browser.find_element(By.ID, "fed-search-big")
        search_bar.clear()
        search_bar.send_keys(target_course.name)
        search_btn = self.browser.find_element(By.ID, "btn-search-tee-time")
        search_btn.click()
        self._pause()

        # WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "search-header-date")))
        # print("Search results rendered.")   

    # def _select_list_view(self) -> None:
    #     list_view_btn = self.browser.find_element(By.XPATH, "//a[@title='List view']")
    #     list_view_btn.click()
    #     self._pause()

    # TODO(vifong)
    def _validate_results(self, target_course: GolfCourse, target_date: datetime.date) -> bool:
        course_result = self.browser.find_element(By.ID, "fedresults").text
        date_result = self.browser.find_element(By.ID, "search-header-date").text
        formatted_date = target_date.strftime("%a, %b %d")
        print("Validating results...")
        print("\ttarget_course:", target_course.name)
        print("\tcourse_result:", course_result)
        print("\tdate_result:", date_result)
        print("\ttarget_date:", formatted_date)
        return target_course == course_result and formatted_date == date_result

    # TODO(vifong)
    def _check_diffs(self) -> bool:
        return True

    def _parse_results(self) -> list[str]:
        html_text = self.browser.page_source
        results = re.findall('<time class=" time-meridian">(.+?)</time>', html_text, re.DOTALL)
        if self.debug_mode:
            print(results)
        if not results:
            return []

        cleaned_times = []
        for result in results:
            cleaned_str = result.strip()
            cleaned_str = re.sub('<script (.+?)</script>', '', cleaned_str)
            cleaned_str = re.sub('<sub>', '', cleaned_str)
            cleaned_str = re.sub('</sub>', '', cleaned_str)
            cleaned_times.append(cleaned_str)

        if self.debug_mode:
            print(cleaned_times)  
        return cleaned_times

    def _snapshot_results(self, target_course: GolfCourse, target_date: datetime.date, results: list[str]) -> None:
        file_name = 'snapshots/{course}_{target_date}.html'.format(
            course=target_course.tag, target_date=target_date.strftime("%Y%m%d"))
        with open(file_name, 'w') as f:
            f.write("Timestamp: {current_date} \n".format(current_date=str(datetime.datetime.now())))
            f.write(results)
            print("Snapshot written to", file_name)


    def _pause(self, secs=1) -> None:
        time.sleep(secs)


class NotificationMessageWriter():
    def __init__(self, results: dict[str, list[tuple[str, list[str]]]], output_file: str) -> None:
        # key: course name
        # value: [(date, [times]), ...]
        self.results = results
        self.output_file = output_file

    def write(self) -> str:
        message = self._craft()
        with open(self.output_file, 'w') as f:
            f.write(message)
            print("Message written to", self.output_file)

    def _craft(self) -> str:
        message = "%0ATee Time Alert!%0A"
        print(self.results.items())
        for course_name, tee_times in self.results.items():
            message += "%0A{course}:%0A".format(course=course_name)
            for date, times in tee_times:
                message += "{date} - {times}%0A".format(date=date, times=times)

        print(message)
        return message


# TODO(vifong)
def compute_target_dates() -> list[datetime.date]:
    return [datetime.date(2023, 5, 27)]


def format_date(date: datetime.date) -> str:
    return date.strftime("%a, %b %d")   


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')
    # TODO(vifong): Don't think this works because it gets reset after Search.
    parser.add_argument("--filter-times", action='store_true')
    args = parser.parse_args()

    target_dates = compute_target_dates()
    scraper = GolfNowScraper(debug_mode=args.debug, filter_times=args.filter_times)

    all_results = defaultdict(list)
    for course in COURSES:
        for date in target_dates:
            times = scraper.scrape(target_course=course, target_date=date, player_count=PLAYER_COUNT)
            if times:
                all_results[course.name].append((format_date(date), str(times)))

    message_writer = NotificationMessageWriter(results=all_results, output_file=MESSAGE_OUTPUT_FILE)
    message_writer.write()

    if args.debug:
        time.sleep(600)

    scraper.close()
