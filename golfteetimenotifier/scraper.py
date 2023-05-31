from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
from queue import Queue
import datetime as dt
import re
import pandas as pd
import pprint
import time
import threading


class GolfCourse(NamedTuple):
    name: str
    tag: str
    id: str


class GolfNowScraper():
    URL_TEMPLATE = (
        "https://www.golfnow.com/tee-times/facility/{course_id}-{course_tag}/search" +
        "#sortby=Date&view=Grouping&holes=3&timeperiod=42&timemax=30&timemin=10&"+ 
        "players=2&pricemax=10000&pricemin=0&promotedcampaignsonly=false")
    COLUMNS = ['Course', 'Date', 'Tee Time', 'Players']
    END_HOUR_9PM = 42
    END_HOUR_3PM = 30

    def __init__(self, earliest_tee_time: dt.time, latest_tee_time: dt.time, min_players: int, 
                       debug_mode=False, all_times=False) -> None:
        self.earliest_tee_time = earliest_tee_time
        self.latest_tee_time = latest_tee_time
        self.min_players = min_players
        self.debug_mode = debug_mode
        self.all_times = all_times
        self.pprinter = pprint.PrettyPrinter(indent=4)
        self.chrome_options = Options()
        if not debug_mode:
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.chrome_options.add_argument("--headless")

    def scrape(self, target_course: GolfCourse, target_date: dt.date) -> pd.DataFrame:
        self._load_landing_page(target_course=target_course)
        self._filter_date(target_date)
        self._filter_course(target_course)
        self._filter_player_count()
        # self._validate_results(target_course=target_course, target_date=target_date)
        return self._parse_results(target_course=target_course, target_date=target_date)
        
    def close(self):
        self.browser.close()

    def _load_landing_page(self, target_course: GolfCourse) -> None:
        url = self.URL_TEMPLATE.format(course_id=target_course.id, course_tag=target_course.tag)            
        self.browser = webdriver.Chrome(options=self.chrome_options)
        self.browser.get(url)
        self.browser.maximize_window()
        self._pause()

    def _filter_player_count(self) -> None:
        golfers_btn = self.browser.find_element(By.XPATH, "//a[@title='Golfers']")
        golfers_btn.click()
        self._pause()

        two_golfers_radio_input = self.browser.find_element(
            By.XPATH, 
            "//input[@type='radio' and @value='{players}']".format(players=self.min_players))
        parent_element = two_golfers_radio_input.find_element(By.XPATH, "..")
        parent_element.click()
        self._pause()

    def _filter_date(self, target_date: dt.date) -> None:
        date_btn = self.browser.find_element(By.ID, "fed-search-big-date")
        date_btn.click()
        self._pause()

        picker_nav_prev = self.browser.find_element(By.CLASS_NAME, "picker__nav--prev")
        picker_nav_next = self.browser.find_element(By.CLASS_NAME, "picker__nav--next")

        # Check the year
        picker_year = self.browser.find_element(By.CLASS_NAME, "picker__year")         
        while picker_year.text != str(target_date.year):
            if self.debug_mode:
                print("target_year:{0}, picker_year:{1}".format(target_date.year, picker_year.text))
            self._pause(2)
            picker_year = self.browser.find_element(By.CLASS_NAME, "picker__year")
            picker_nav_next = self.browser.find_element(By.CLASS_NAME, "picker__nav--next")
        if self.debug_mode:
            print("target_year:{0}, picker_year:{1}".format(target_date.year, picker_year.text))

        # Check the month
        month = '{0:%B}'.format(target_date)
        picker_month = self.browser.find_element(By.CLASS_NAME, "picker__month")
        picker_month_date_object = dt.datetime.strptime(picker_month.text, '%B')
        # Increase month
        while picker_month_date_object.month < target_date.month:
            if self.debug_mode:
                print("target_month:{0}, picker_month:{1}".format(month, picker_month.text))
            picker_nav_next.click()
            self._pause()
            picker_nav_next = self.browser.find_element(By.CLASS_NAME, "picker__nav--next")
            picker_month = self.browser.find_element(By.CLASS_NAME, "picker__month")
            picker_month_date_object = dt.datetime.strptime(picker_month.text, '%B')
        # Decrease month
        while picker_month_date_object.month > target_date.month:
                if self.debug_mode:
                        print("target_month:{0}, picker_month:{1}".format(month, picker_month.text))
                picker_nav_prev.click()
                self._pause()
                picker_month = self.browser.find_element(By.CLASS_NAME, "picker__month")
                picker_month_date_object = dt.datetime.strptime(picker_month.text, '%B')
        if self.debug_mode:
                print("target_month:{0}, picker_month:{1}".format(month, picker_month.text))

        # Select the day
        picker_day = self.browser.find_element(
            By.XPATH, "//div[@aria-label='{date}']".format(date=target_date.strftime("%a, %b %d")))
        if self.debug_mode:
                print("target_day:{0}, picker_day:{1}".format(target_date.day, picker_day.text))
        picker_day.click()
        self._pause()

    def _filter_course(self, target_course: GolfCourse) -> None:
        search_bar = self.browser.find_element(By.ID, "fed-search-big")
        search_bar.clear()
        search_bar.send_keys(target_course.name)
        search_btn = self.browser.find_element(By.ID, "btn-search-tee-time")
        search_btn.click()
        self._pause()

    # TODO(vifong)
    def _validate_results(self, target_course: GolfCourse, target_date: dt.date) -> bool:
        course_result = self.browser.find_element(By.ID, "fedresults").text
        date_result = self.browser.find_element(By.ID, "search-header-date").text
        formatted_date = target_date.strftime("%a, %b %d")
        print("Validating results...")
        print("\ttarget_course:", target_course.name)
        print("\tcourse_result:", course_result)
        print("\tdate_result:", date_result)
        print("\ttarget_date:", formatted_date)
        return target_course == course_result and formatted_date == date_result

    def _parse_results(self, target_course: GolfCourse, target_date: dt.date) -> pd.DataFrame: 
        html_text = self.browser.page_source
        tee_time_results = re.findall('<a href="/tee-times/facility(.+?)</a>', html_text, re.DOTALL)
        df_data = []
        for raw_result in tee_time_results:
            time = self._clean_time_result(raw_result)
            player_count = self._clean_players_result(raw_result)
            if time == "" or player_count == "":
                continue
            if (time >= self.earliest_tee_time and time <= self.latest_tee_time) or self.all_times:
                df_data.append([target_course.name, target_date, time, player_count])
        return pd.DataFrame(df_data, columns=self.COLUMNS)

    def _clean_time_result(self, raw_result: str) -> str:
        time_result_list = re.findall(
            '<time class=" time-meridian">(.+?)</time>', raw_result, re.DOTALL)
        if len(time_result_list) == 0:
            return ""
        cleaned_str = time_result_list[0].strip()
        cleaned_str = re.sub('<script (.+?)</script>', '', cleaned_str)
        cleaned_str = re.sub('<sub>', '', cleaned_str)
        cleaned_str = re.sub('</sub>', '', cleaned_str)
        cleaned_str = re.sub('\'', '', cleaned_str)
        return dt.datetime.strptime(cleaned_str, "%I:%M%p").time()

    def _clean_players_result(self, raw_result: str) -> str:
        players_result_list = re.findall(
            '<span class="golfers-available" title="Golfers">(.+?)</span>', 
            raw_result, re.DOTALL)
        if len(players_result_list) == 0:
            return ""
        cleaned_str = players_result_list[0].strip()
        cleaned_str = re.sub('<i (.+?)</i>', '', cleaned_str)
        return cleaned_str[-1]

    def _pause(self, secs=1) -> None:
        time.sleep(secs)


class ScrapeThread(threading.Thread):
    def __init__(self, target_course: GolfCourse, target_dates: List[dt.date], 
                       min_players: int, earliest_tee_time: dt.time, latest_tee_time: dt.time,
                       results_queue: Queue, debug_mode=False, all_times=False) -> None:
        threading.Thread.__init__(self)
        self.target_course = target_course
        self.target_dates = target_dates
        self.min_players = min_players
        self.earliest_tee_time = earliest_tee_time
        self.latest_tee_time = latest_tee_time
        self.debug_mode = debug_mode
        self.all_times = all_times
        self.results_queue = results_queue

    def run(self) -> None:
        print("Running {course} thread...".format(course=self.target_course.tag))
        scraper = GolfNowScraper(min_players=self.min_players, 
                                 earliest_tee_time=self.earliest_tee_time, 
                                 latest_tee_time=self.latest_tee_time,
                                 debug_mode=self.debug_mode,
                                 all_times=self.all_times)
        for date in self.target_dates:
            print("Thread {course} scraping {date}...".format(
                course=self.target_course.tag, date=date))
            tee_times_df = scraper.scrape(target_course=self.target_course, target_date=date)
            print(tee_times_df)
            if not tee_times_df.empty:
                self.results_queue.put(tee_times_df)

        scraper.close()

