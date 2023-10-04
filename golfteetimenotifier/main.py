import argparse
import calendar
import datetime as dt
import pandas as pd
import time

from message_writer import NotificationMessageWriter
from queue import Queue
from scraper import GolfCourse
from scraper import GolfNowScraper
from scraper import ScrapeThread
from snapshot_handler import SnapshotHandler
from typing import List


DATE_WINDOW = 7
EARLIEST_TEE_TIME = dt.time(7, 45)  # 7:45am
LATEST_TEE_TIME = dt.time(16, 0)   # 4pm
MIN_PLAYERS = 2
COURSES = [
    GolfCourse('Rancho Park Golf Course', 'rancho-park-golf-course', '12203'),
    GolfCourse('Woodley Lakes Golf Course', 'woodley-lakes-golf-course', '12205'),
    GolfCourse('Balboa Golf Course', 'balboa-golf-course', '12197'),
    GolfCourse('Encino Golf Course', 'encino-golf-course', '12200'),
    # GolfCourse('Hansen Dam Golf Course', 'hansen-dam-golf-course', '12201'),
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
            if candidate_date != now.date() or now.time() < LATEST_TEE_TIME:
                weekends.append(candidate_date)
        candidate_date = candidate_date + dt.timedelta(1)

    print("target_dates:", weekends)
    return weekends


def run_scrape(target_dates: List[dt.date], debug_mode: bool, all_times: bool) -> Queue:
    results_queue = Queue()
    threads = []
    for course in COURSES:
        t = ScrapeThread(target_course=course, target_dates=target_dates, min_players=MIN_PLAYERS,
                         earliest_tee_time=EARLIEST_TEE_TIME, latest_tee_time=LATEST_TEE_TIME,
                         results_queue=results_queue, debug_mode=debug_mode, all_times=all_times)
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
    return aggregated_df


if __name__ == '__main__':
    # Setup flags.
    args = init_args()

    print('min_players:', MIN_PLAYERS)
    print('latest_tee_time:', LATEST_TEE_TIME)
    print('earliest_tee_time:', EARLIEST_TEE_TIME)

    # Prepare and run scrape and collect results.
    target_dates = compute_target_dates()
    results_queue = run_scrape(
        target_dates=target_dates, debug_mode=args.debug, all_times=args.all_times)
    aggregated_df = aggregate_results(results_queue)
    print("\n==AGGREGATED DATA==\n", aggregated_df)

    snapshot_handler = SnapshotHandler(data_df=aggregated_df)    
    snapshot_handler.write_snapshot_df()
    
    # Compare snapshots to determine whether to send a notification.
    message_writer = NotificationMessageWriter(data_df=aggregated_df)
    if snapshot_handler.has_new_tee_times():
        message_writer.write()
    else:
        message_writer.delete()
