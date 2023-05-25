from collections import defaultdict
from message_writer import NotificationMessageWriter
from snapshot_handler import delete_stale_snapshots
from snapshot_handler import snapshot_results
from snapshot_handler import SnapshotDiffer
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
from scraper import GolfCourse
from scraper import GolfNowScraper
from scraper import ScrapeThread
from shutil import rmtree
import argparse
import datetime
import time


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


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')
    # TODO(vifong): Don't think this works because it gets reset after Search.
    parser.add_argument("--filter-times", action='store_true')
    return parser.parse_args()


def compute_target_dates() -> List[datetime.date]:
    weekends = []
    today = datetime.date.today()
    last_date = today + datetime.timedelta(NUM_DAYS_AHEAD)
    candidate_date = today
    while candidate_date <= last_date:
        if candidate_date.weekday() in [calendar.SATURDAY, calendar.SUNDAY]:
            weekends.append(candidate_date)
        candidate_date = candidate_date + datetime.timedelta(1)
    print("target_dates:", d)
    return weekends

def run_scrape(target_dates: List[datetime.date], debug_mode: bool, filter_times: bool) -> Queue:
    results_queue = Queue()
    threads = []
    for course in COURSES:
        t = ScrapeThread(
            target_course=course, target_dates=target_dates, player_count=PLAYER_COUN
            accumulated_results=results_queue, debug_mode=debug_mode, filter_times=filter_times)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return results_queue


def aggregate_results(results_queue: Queue) 
        -> Dict[str, List[Tuple[datetime.date, List[datetime.date]]]]:
    aggregated_results = defaultdict(list)
    while not results_queue.empty():
        aggregated_results.update(results_queue.get())
    if args.debug:
        print(aggregated_results)
    return aggregated_results



# To-dos:
# State checking -> notifications
# Add a way to ignore a date
if __name__ == '__main__':
    # Setup environment.
    args = init_args()
    delete_stale_snapshots()

    # Prepare and run scrape and collect results.
    target_dates = compute_target_dates()
    results_queue = run_scrape(
        target_dates=target_dates, debug_mode=args.debug, filter_times=args.filter_times)
    aggregated_results = aggregated_results(results_queue)

    # Compare state and snapshot results. Determine whether to send notification.
    snapshot_differ = SnapshotDiffer(aggregated_results)
    snapshot_differ.has_new_times()

    # Write notification message.
    # message_writer = NotificationMessageWriter(results=accumulated_results, output_file=MESSAGE_OUTPUT_FILE)
    # message_writer.write()

    if args.debug:
        time.sleep(600)