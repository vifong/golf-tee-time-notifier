from scraper import GolfCourse
from shutil import rmtree
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
import datetime
import json
import os


SNAPSHOTS_DIR = "output/snapshots"
TMP_SUBDIR = os.path.join(SNAPSHOTS_DIR, "tmp")


class SnapshotHandler():
    def __init__(self, aggregated_results: (
            Dict[datetime.date, List[Tuple[GolfCourse, List[datetime.date]]]])) -> None:
        self.aggregated_results = aggregated_results

    def clean_stale_snapshots(self) -> None:
        if os.path.exists(TMP_SUBDIR):
            rmtree(TMP_SUBDIR)

        today = datetime.date.today()
        for _, _, json_files in os.walk(SNAPSHOTS_DIR):
            for f in json_files:
                file_path = os.path.join(SNAPSHOTS_DIR, f)
                snapshot_date = datetime.datetime.strptime(f.replace('.json', ''), "%Y%m%d")
                # Delete directories of dates that already passed
                if snapshot_date.date() < today:
                    print("Deleting", file_path)
                    rmtree(file_path)

    def diff_snapshots(self) -> None:
        pass

    def snapshot_results(self, is_tmp=True) -> None:
        for date, results in self.aggregated_results.items():
            json_data = self._convert_to_json_data(results)
            dir_path = TMP_SUBDIR if is_tmp else SNAPSHOTS_DIR 
            self._write_json_to_file(dir_path=dir_path, target_date=date, json_data=json_data)

    def _write_json_to_file(self, dir_path: str,
                                  target_date: datetime.date, 
                                  json_data: Dict[str, List[str]]) -> None:
        if not os.path.exists(dir_path):
            print("Initializing", dir_path)
            os.mkdir(dir_path)

        snapshot_path = self._build_snapshot_path(dir_path=dir_path, target_date=target_date)
        with open(snapshot_path, 'w') as f:
            f.write(json.dumps(json_data, indent=2))
            print("Snapshot written to", snapshot_path)

    def _convert_to_json_data(
        self, results: List[Tuple[GolfCourse, List[datetime.date]]]) -> Dict[str, List[str]]:
        json_data = {}
        for course, tee_times in results:
            json_data[course.tag] = [ t.strftime("%H:%M") for t in tee_times ]
        return json_data

    def _build_snapshot_path(self, dir_path: str, target_date: datetime.date):
        return os.path.join(dir_path, "{date}.json".format(date=target_date.strftime("%Y%m%d")))



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




