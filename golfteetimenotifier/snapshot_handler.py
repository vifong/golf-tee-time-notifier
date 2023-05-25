from scraper import GolfCourse
from shutil import rmtree
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
import datetime
import json
import os


SNAPSHOTS_DIRECTORY = "output/snapshots"


class SnapshotHandler():
    def __init__(self) -> None:
        pass

    def delete_stale_snapshots(self) -> None:
        today = datetime.date.today()
        for _, subdirs, _ in os.walk(SNAPSHOTS_DIRECTORY):
            for subdir in subdirs:
                dir_path = os.path.join(SNAPSHOTS_DIRECTORY, subdir)
                snapshot_date = datetime.datetime.strptime(subdir, "%Y%m%d")
                # Delete directories of dates that already passed
                if snapshot_date.date() < today:
                    print("Deleting", dir_path)
                    rmtree(dir_path)

    def compare_snapshots(self) -> None:
        pass

    def snapshot_results(self, aggregated_results: (
            Dict[datetime.date, List[Tuple[GolfCourse, List[datetime.date]]]])) -> None:
        for date, results in aggregated_results.items():
            json_data = self._convert_to_json_data(results)
            self._write_json_to_file(target_date=date, json_data=json_data)


    def _write_json_to_file(self, target_date: datetime.date, 
                                  json_data: Dict[str, List(str)]) -> None:
        snapshot_path = os.path.join(
            SNAPSHOTS_DIRECTORY, "{date}.json".format(date=target_date.strftime("%Y%m%d")))
        with open(snapshot_path, 'w') as f:
            f.write(json.dumps(json_data, indent=2))
            print("Snapshot written to", file_path)

    def _convert_to_json_data(
        self, results: List[Tuple[GolfCourse, List[datetime.date]]]) -> Dict[str, List(str)]:
        json_data = {}
        for course, tee_times in results:
            json_data[course.tag] = [ t.strftime("%H:%M") for t in tee_times ]
        return json_data









def snapshot_results(results: Dict[datetime.date, List[Tuple[GolfCourse, List[datetime.date]]]],
                     target_date: datetime.date) -> None:
    
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


# def snapshot_results(target_course: GolfCourse, target_date: datetime.date, 
#                      results: List[datetime.date]) -> None:
#     metadata = {
#         "course": course.tag,
#         "target_date": str(target_date),
#         "timestamp": str(datetime.datetime.now()),
#         "tee_times": [ t.strftime("%H:%M") for t in results ]
#     }
#     subdir = "{root}/{target_date}".format(
#         root=SNAPSHOTS_DIRECTORY, target_date=target_date.strftime("%Y%m%d"))
#     if not os.path.exists(subdir):
#         print("Creating directory", subdir)
#         os.makedirs(subdir)
#     file_path = os.path.join(subdir, "{course}.json".format(course=target_course.tag))
#     with open(file_path, 'w') as f:
#         f.write(json.dumps(metadata, indent=2))
#         print("Snapshot written to", file_path)


class SnapshotDiffer():
  def __init__(self, results: Dict[datetime.date, 
                                   List[Tuple[GolfCourse, List[datetime.date]]]]) -> None:
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




