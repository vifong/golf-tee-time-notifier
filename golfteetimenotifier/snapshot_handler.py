from scraper import GolfCourse
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
import datetime
import json
import os


SNAPSHOTS_DIRECTORY = "output/snapshots"


def delete_stale_snapshots() -> None:
    today = datetime.date.today()
    for _, subdirs, _ in os.walk(SNAPSHOTS_DIRECTORY):
    for subdir in subdirs:
        dir_path = os.path.join(SNAPSHOTS_DIRECTORY, subdir)
        snapshot_date = datetime.datetime.strptime(subdir, "%Y%m%d")
        # Delete directories of dates that already passed
        if snapshot_date.date() < today:
            print("Deleting", dir_path)
            rmtree(dir_path)


def snapshot_results(target_course: GolfCourse, target_date: datetime.date, 
                     results: List[datetime.date]) -> None:
    metadata = {
        "course": course.tag,
        "target_date": str(target_date),
        "timestamp": str(datetime.datetime.now()),
        "tee_times": [ t.strftime("%H:%M") for t in results ]
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


class SnapshotDiffer():
  def __init__(self, results: Dict[str, List[Tuple[datetime.date, List[datetime.date]]]]) -> None:
      self.results = results

  def has_new_times(self) -> bool:
    for course_name, tee_times in results.items():
      for date, _ in tee_times:
        snapshot_path = "{root}/{date}/{course_tag}.json".format(
            root=SNAPSHOTS_DIRECTORY, date=date.strftime("%Y%m%d"), 
            course_tag=course_name.lower().replace(' ', '-'))
        self._has_new_times(snapshot_path)
    #         if self._has_new_times(snapshot_path):
    #             return True
    # return False

  def _has_new_times(self, snapshot_path: str) -> bool:
      with open(snapshot_path) as f:
          data = json.load(f)
          print(data)
          f.close()

  # def _parse_json(self, snapshot_path: str):




