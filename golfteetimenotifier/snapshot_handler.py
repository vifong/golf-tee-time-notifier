from collections import OrderedDict
from scraper import GolfCourse
from shutil import rmtree
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
import datetime as dt
import filecmp
import json
import os
import pandas as pd


SNAPSHOTS_DIR = "output/snapshots"
TMP_SUBDIR = os.path.join(SNAPSHOTS_DIR, "tmp")


class SnapshotHandler():
    def __init__(self, aggregated_results: pd.DataFrame) -> None:
        self.aggregated_results = aggregated_results
        self.clean_stale_snapshots()

    def clean_stale_snapshots(self) -> None:
        if os.path.exists(TMP_SUBDIR):
            rmtree(TMP_SUBDIR)

        today = dt.date.today()
        for _, _, json_files in os.walk(SNAPSHOTS_DIR):
            for f in json_files:
                file_path = os.path.join(SNAPSHOTS_DIR, f)
                snapshot_date = dt.datetime.strptime(f.replace('.json', ''), "%Y%m%d")
                # Delete directories of dates that already passed
                if snapshot_date.date() < today:
                    print("Deleting", file_path)
                    rmtree(file_path)

    def snapshot_results(self, is_tmp=True) -> None:
        for date, results in self.aggregated_results.items():
            json_data = self._convert_to_json_data(results)
            dir_path = TMP_SUBDIR if is_tmp else SNAPSHOTS_DIR 
            self._write_json_to_file(dir_path=dir_path, target_date=date, json_data=json_data)


    # Maybe the better way to handle snapshots is to just snapshot the content sent for notification
    # and compare with that. Rather than comparing with the previous run.
    def diff_snapshots(self) -> None:
        for _, _, tmp_files in os.walk(TMP_SUBDIR):
            print(tmp_files)
            for file_name in tmp_files:
                tmp_snapshot = os.path.join(TMP_SUBDIR, file_name)
                prev_snapshot = os.path.join(SNAPSHOTS_DIR, file_name)
                if self._has_diffs(path1=tmp_snapshot, path2=prev_snapshot):
                    print("{0} has diffs!".format(file_name))

                else:
                    print("{0} and {1} are the same.".format(tmp_snapshot, prev_snapshot))


    def _extract_diffs(self, path1: str, path2: str) -> str:
        pass

    def _has_diffs(self, path1: str, path2: str) -> bool:
        return not filecmp.cmp(path1, path2)


    def _write_json_to_file(self, dir_path: str,
                                  target_date: dt.date, 
                                  json_data: Dict[str, List[str]]) -> None:
        if not os.path.exists(dir_path):
            print("Initializing", dir_path)
            os.mkdir(dir_path)

        snapshot_path = self._build_snapshot_path(dir_path=dir_path, target_date=target_date)
        with open(snapshot_path, 'w') as f:
            f.write(json.dumps(json_data, indent=2))
            print("Snapshot written to", snapshot_path)

    def _convert_to_json_data(
        self, results: List[Tuple[GolfCourse, List[dt.date]]]) -> Dict[str, List[str]]:
        json_data = OrderedDict()
        sorted_results = sorted(results)
        for course, tee_times in sorted_results:
            json_data[course.tag] = [ t.strftime("%H:%M") for t in tee_times ]
        return json_data

    def _build_snapshot_path(self, dir_path: str, target_date: dt.date):
        return os.path.join(dir_path, "{date}.json".format(date=target_date.strftime("%Y%m%d")))



# class SnapshotDiffer():
#   def __init__(self, results: Dict[dt.date, 
#                                    List[Tuple[GolfCourse, List[dt.date]]]]) -> None:
#       self.results = results

#   def has_new_times(self) -> bool:
#     for course_name, tee_times in results.items():
#       for date, _ in tee_times:
#         snapshot_path = "{root}/{date}/{course_tag}.json".format(
#             root=SNAPSHOTS_DIRECTORY, date=date.strftime("%Y%m%d"), 
#             course_tag=course_name.lower().replace(' ', '-'))
#         self._has_new_times(snapshot_path)
#     #         if self._has_new_times(snapshot_path):
#     #             return True
#     # return False

#   def _has_new_times(self, snapshot_path: str) -> bool:
#       with open(snapshot_path) as f:
#           data = json.load(f)
#           print(data)
#           f.close()

#   # def _parse_json(self, snapshot_path: str):




