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
import datetime
import time


DATE_WINDOW = 7
PLAYER_COUNT = 2
LATEST_HOUR = 17
COURSES = [
    # GolfCourse('Rancho Park Golf Course', 'rancho-park-golf-course', '12203', ),
    GolfCourse('Woodley Lakes Golf Course', 'woodley-lakes-golf-course', '12205' ),
    GolfCourse('Balboa Golf Course', 'balboa-golf-course', '12197'),
    # GolfCourse('Encino Golf Course', 'encino-golf-course', '12200'),
    GolfCourse('Hansen Dam Golf Course', 'hansen-dam-golf-course', '12201'),
]


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')
    # TODO(vifong): Don't think this works because it gets reset after Search.
    parser.add_argument("--filter-times", action='store_true')
    return parser.parse_args()


def compute_target_dates() -> List[datetime.date]:
    weekends = []
    today = datetime.date.today()
    last_date = today + datetime.timedelta(DATE_WINDOW)
    candidate_date = today
    while candidate_date <= last_date:
        if candidate_date.weekday() in [calendar.SATURDAY, calendar.SUNDAY]:
            weekends.append(candidate_date)
        candidate_date = candidate_date + datetime.timedelta(1)
    print("target_dates:", weekends)
    return weekends


def run_scrape(target_dates: List[datetime.date], debug_mode: bool, filter_times: bool) -> Queue:
    results_queue = Queue()
    threads = []
    for course in COURSES:
        t = ScrapeThread(target_course=course, target_dates=target_dates, player_count=PLAYER_COUNT,
                         latest_hour=LATEST_HOUR, results_queue=results_queue, 
                         debug_mode=debug_mode, filter_times=filter_times)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return results_queue


def aggregate_results(results_queue: Queue) -> (
        Dict[datetime.date, List[Tuple[GolfCourse, List[datetime.date]]]]):
    aggregated_results = defaultdict(list)
    while not results_queue.empty():
        course, date, times = results_queue.get()
        aggregated_results[date].append((course, times))
    if args.debug:
        print("\naggregated_results:\n", aggregated_results)
    return aggregated_results


# To-dos:
# State checking -> notifications
# Add a way to ignore a date
if __name__ == '__main__':
    # Setup flags.
    args = init_args()

    # Prepare and run scrape and collect results.
    target_dates = compute_target_dates()
    results_queue = run_scrape(
        target_dates=target_dates, debug_mode=args.debug, filter_times=args.filter_times)
    aggregated_results = aggregate_results(results_queue)

    # Compare snapshots to determine whether to send a notification.
    snapshot_handler = SnapshotHandler(aggregated_results)    
    snapshot_handler.snapshot_results()   
    snapshot_handler.diff_snapshots() 

    # Write notification message.
    # message_writer = NotificationMessageWriter(results=accumulated_results, output_file=MESSAGE_OUTPUT_FILE)
    # message_writer.write()

    if args.debug:
        time.sleep(600)