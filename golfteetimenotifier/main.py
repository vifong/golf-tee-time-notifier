from collections import defaultdict
from message_writer import NotificationMessageWriter
from snapshot_handler import SnapshotHandler
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
from scraper import GolfCourse
from scraper import GolfNowScraper
from scraper import ScrapeThread
from shutil import rmtree
from queue import Queue
import argparse
import calendar
import datetime as dt
import pandas as pd
import time


DATE_WINDOW = 7
PLAYER_COUNT = 2
LATEST_HOUR = 17    # Before 5pm
COURSES = [
    GolfCourse('Rancho Park Golf Course', 'rancho-park-golf-course', '12203', ),
    GolfCourse('Woodley Lakes Golf Course', 'woodley-lakes-golf-course', '12205' ),
    GolfCourse('Balboa Golf Course', 'balboa-golf-course', '12197'),
    GolfCourse('Encino Golf Course', 'encino-golf-course', '12200'),
    GolfCourse('Hansen Dam Golf Course', 'hansen-dam-golf-course', '12201'),
]


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')
    parser.add_argument("--all-times", action='store_true')
    return parser.parse_args()


def compute_target_dates() -> List[dt.date]:
    now = dt.datetime.now()
    last_date = now.date() + dt.timedelta(DATE_WINDOW)
    candidate_date = now.date()

    weekends = []
    while candidate_date <= last_date:
        if candidate_date.weekday() in [calendar.SATURDAY, calendar.SUNDAY]:
            # Skip today if it's already too late.
            if candidate_date != now.date() or now.time().hour < LATEST_HOUR:
                weekends.append(candidate_date)
        candidate_date = candidate_date + dt.timedelta(1)

    print("target_dates:", weekends)
    return weekends


def run_scrape(target_dates: List[dt.date], debug_mode: bool, all_times: bool) -> Queue:
    results_queue = Queue()
    threads = []
    for course in COURSES:
        t = ScrapeThread(target_course=course, target_dates=target_dates, player_count=PLAYER_COUNT,
                         latest_hour=LATEST_HOUR, results_queue=results_queue, 
                         debug_mode=debug_mode, all_times=all_times)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return results_queue


def aggregate_results(results_queue: Queue) -> pd.DataFrame:
    aggregated_df = pd.DataFrame()
    while not results_queue.empty():
        course_df = results_queue.get()
        aggregated_df = pd.concat([aggregated_df, course_df], ignore_index=True)
    if args.debug:
        print("\naggregated_results:\n", aggregated_df)
    return aggregated_df


if __name__ == '__main__':
    # Setup flags.
    args = init_args()

    # Prepare and run scrape and collect results.
    target_dates = compute_target_dates()
    results_queue = run_scrape(
        target_dates=target_dates, debug_mode=args.debug, all_times=args.all_times)
    aggregated_df = aggregate_results(results_queue)

    print(aggregated_df)

    # Compare snapshots to determine whether to send a notification.
    snapshot_handler = SnapshotHandler(data_df=aggregated_df)    
    snapshot_handler.has_new_tee_times()

    message_writer = NotificationMessageWriter(data_df=aggregated_df)
    if snapshot_handler.has_new_tee_times():
        message_writer.write()
    else:
        message_writer.delete()

    if args.debug:
        time.sleep(600)