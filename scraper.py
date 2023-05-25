from collections import defaultdict
from queue import Queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from shutil import rmtree
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
import argparse
import calendar
import datetime
import json
import os
import re
import time
import threading


class GolfCourse(NamedTuple):
    id: str
    tag: str
    name: str


SNAPSHOTS_DIRECTORY = "snapshots"
MESSAGE_OUTPUT_FILE = "message.txt"
NUM_DAYS_AHEAD = 7
PLAYER_COUNT = 2
LATEST_HOUR = 17
COURSES = [
    GolfCourse('12203', 'rancho-park-golf-course', 'Rancho Park Golf Course'),
    GolfCourse('12205', 'woodley-lakes-golf-course', 'Woodley Lakes Golf Course'),
    GolfCourse('12197', 'balboa-golf-course', 'Balboa Golf Course'),
    GolfCourse('12200', 'encino-golf-course', 'Encino Golf Course'),
    GolfCourse('12201', 'hansen-dam-golf-course', 'Hansen Dam Golf Course'),
]

# To-dos:
# State checking -> notifications
# Add a way to ignore a date

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
        self.chrome_options = Options()
        if not debug_mode:
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.chrome_options.add_argument("--headless")

    def scrape(self, target_course: GolfCourse, target_date: datetime.date, player_count: int) -> List[str]:
        self._load_landing_page(target_course=target_course, player_count=player_count)
        self._filter_date(target_date=target_date)
        self._filter_course(target_course=target_course)
        self._filter_player_count(player_count=player_count)
        # self._validate_results(target_course=target_course, target_date=target_date)
        # self._select_list_view()
        results = self._parse_results()
        self._snapshot_results(target_course=target_course, target_date=target_date, results=results)
        return results

    def close(self):
        self.browser.close()

    def _load_landing_page(self, target_course: GolfCourse, player_count: int) -> None:
        url = self.URL_TEMPLATE.format(course_id=target_course.id, 
                                       course_tag=target_course.tag,
                                       end_hour=self.END_HOUR_3PM if self.filter_times else self.END_HOUR_9PM,
                                       player_count=PLAYER_COUNT)       
        self.browser = webdriver.Chrome(options=self.chrome_options)
        self.browser.get(url)
        self.browser.maximize_window()
        self._pause()

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

        picker_nav_prev = self.browser.find_element(By.CLASS_NAME, "picker__nav--prev")
        picker_nav_next = self.browser.find_element(By.CLASS_NAME, "picker__nav--next")

        # Check the year
        picker_year = self.browser.find_element(By.CLASS_NAME, "picker__year")     
        while picker_year.text != str(target_date.year):
            if self.debug_mode:
                print("target_year: {0}, picker_year: {1}".format(target_date.year, picker_year.text))
            self._pause(2)
            picker_year = self.browser.find_element(By.CLASS_NAME, "picker__year")
            picker_nav_next = self.browser.find_element(By.CLASS_NAME, "picker__nav--next")
        if self.debug_mode:
            print("target_year: {0}, picker_year: {1}".format(target_date.year, picker_year.text))

        # Check the month
        month = '{0:%B}'.format(target_date)
        picker_month = self.browser.find_element(By.CLASS_NAME, "picker__month")
        picker_month_date_object = datetime.datetime.strptime(picker_month.text, '%B')
        # Increase month
        while picker_month_date_object.month < target_date.month:
            if self.debug_mode:
                print("target_month: {0}, picker_month: {1}".format(month, picker_month.text))
            picker_nav_next.click()
            self._pause()
            picker_nav_next = self.browser.find_element(By.CLASS_NAME, "picker__nav--next")
            picker_month = self.browser.find_element(By.CLASS_NAME, "picker__month")
            picker_month_date_object = datetime.datetime.strptime(picker_month.text, '%B')
        # Decrease month
        while picker_month_date_object.month > target_date.month:
            if self.debug_mode:
                print("target_month: {0}, picker_month: {1}".format(month, picker_month.text))
            picker_nav_prev.click()
            self._pause()
            picker_month = self.browser.find_element(By.CLASS_NAME, "picker__month")
            picker_month_date_object = datetime.datetime.strptime(picker_month.text, '%B')
        if self.debug_mode:
            print("target_month: {0}, picker_month: {1}".format(month, picker_month.text))

        # Select the day
        picker_day = self.browser.find_element(By.XPATH, "//div[@aria-label='{date}']".format(date=target_date.strftime("%a, %b %d")))
        if self.debug_mode:
            print("target_day: {0}, picker_day: {1}".format(target_date.day, picker_day.text))
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

    def _parse_results(self) -> List[datetime.date]:
        html_text = self.browser.page_source
        results = re.findall('<time class=" time-meridian">(.+?)</time>', html_text, re.DOTALL)
        if not results:
            return []

        times = []
        for result in results:
            cleaned_str = result.strip()
            cleaned_str = re.sub('<script (.+?)</script>', '', cleaned_str)
            cleaned_str = re.sub('<sub>', '', cleaned_str)
            cleaned_str = re.sub('</sub>', '', cleaned_str)
            cleaned_str = re.sub('\'', '', cleaned_str)
            time = datetime.datetime.strptime(cleaned_str, "%I:%M%p")

            # TODO(vifong): Filter out times after 5pm
            if time.hour < LATEST_HOUR:
                times.append(time)

        if self.debug_mode:
            print(times)  
        return times

    def _snapshot_results(self, target_course: GolfCourse, target_date: datetime.date, results: List[datetime.date]) -> None:
        print(results)
        metadata = {
            "course": course.tag,
            "target_date": str(target_date),
            "timestamp": str(datetime.datetime.now()),
            "tee_times": [ t.strftime("%H:%M") for t in results]
        }
        subdir = "{root}/{target_date}".format(
            root=SNAPSHOTS_DIRECTORY, target_date=target_date.strftime("%Y%m%d"))
        if not os.path.exists(subdir):
            print("Creating directory", subdir)
            os.makedirs(subdir)
        file_path = os.path.join(subdir, "{course}.json".format(course=target_course.tag))
        with open(file_path, 'w') as f:
            f.write(json.dumps(metadata, indent=2))
            print("Snapshot written to", file_path)


    def _pause(self, secs=1) -> None:
        time.sleep(secs)


class NotificationMessageWriter():
    def __init__(self, results: Dict[str, List[Tuple[datetime.date, List[datetime.date]]]], output_file: str) -> None:
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
        message = "***Tee Times Alert!***\n"
        for course_name, tee_times in self.results.items():
            message += "\n{course}\n".format(course=self._format_course_name(course_name))
            for date, times in tee_times:
                message += "{date} {times}\n".format(
                    date=format_date(date), times=self._format_times(times))

        print(message)
        return message

    def _format_course_name(self, course_name) -> str:
        return course_name.replace(" Golf Course", '').upper()

    def _format_times(self, times: List[datetime.date]) -> str:
        formatted_times = []
        for t in times:
            formatted_time = t.strftime("%I:%M%p")
            if formatted_time[0] == '0':
                formatted_time = formatted_time[0:]
            formatted_times.append(formatted_time)

        return str(formatted_times).replace(' ', '')


class ScrapeThread(threading.Thread):
    def __init__(self, target_course: GolfCourse, target_dates: List[datetime.date], player_count: int,
                       accumulated_results: Queue, debug_mode=False, filter_times=False) -> None:
        threading.Thread.__init__(self)
        self.target_course = target_course
        self.target_dates = target_dates
        self.player_count = player_count
        self.debug_mode = debug_mode
        self.filter_times = filter_times
        self.results_queue = results_queue

    def run(self) -> None:
        print("Running {course} thread...".format(course=self.target_course.name))
        scraper = GolfNowScraper(debug_mode=args.debug, filter_times=args.filter_times)
        results = defaultdict(list)
        for date in target_dates:
            print("Thread {course} scraping {date}...".format(course=self.target_course.tag, date=date))
            times = scraper.scrape(target_course=self.target_course, target_date=date, player_count=self.player_count)
            if times:
                results[self.target_course.name].append((date, times))
        self.results_queue.put(results)
        scraper.close()


def compute_target_dates() -> List[datetime.date]:
    weekends = []
    today = datetime.date.today()
    last_date = today + datetime.timedelta(NUM_DAYS_AHEAD)
    candidate_date = today
    while candidate_date <= last_date:
        if candidate_date.weekday() in [calendar.SATURDAY, calendar.SUNDAY]:
            weekends.append(candidate_date)
        candidate_date = candidate_date + datetime.timedelta(1)
    print("target_dates:", [format_date(d) for d in weekends])
    return weekends


def format_date(date: datetime.date) -> str:
    return date.strftime("%a, %b %d")   


def delete_stale_snapshots() -> None:
    today = datetime.date.today()
    for _, subdirs, _ in os.walk(SNAPSHOTS_DIRECTORY):
        for subdir in subdirs:
            dir_path = os.path.join(SNAPSHOTS_DIRECTORY, subdir)
            date = datetime.datetime.strptime(subdir, "%Y%m%d")
            # Delete directories of dates that already passed
            print("{0} (date) vs. {1} (today)".format(date.date(), today))
            if date.date() < today:
                print("Deleting", dir_path)
                rmtree(dir_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')
    # TODO(vifong): Don't think this works because it gets reset after Search.
    parser.add_argument("--filter-times", action='store_true')
    args = parser.parse_args()

    delete_stale_snapshots()
    target_dates = compute_target_dates()

    results_queue = Queue()
    threads = []
    for course in COURSES:
        t = ScrapeThread(
            target_course=course, target_dates=target_dates, player_count=PLAYER_COUNT, 
            accumulated_results=results_queue, debug_mode=args.debug, filter_times=args.filter_times)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    accumulated_results = defaultdict(list)
    while not results_queue.empty():
        accumulated_results.update(results_queue.get())

    if args.debug:
        print(accumulated_results)

    message_writer = NotificationMessageWriter(results=accumulated_results, output_file=MESSAGE_OUTPUT_FILE)
    message_writer.write()

    if args.debug:
        time.sleep(600)

