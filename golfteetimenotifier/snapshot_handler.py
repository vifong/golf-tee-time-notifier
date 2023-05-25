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
import numpy as np
import os
import pandas as pd
import pickle


SNAPSHOTS_DIR = "output/snapshots"
TMP_SUBDIR = os.path.join(SNAPSHOTS_DIR, "tmp")


class SnapshotHandler():
    def __init__(self, data_df: pd.DataFrame) -> None:
        self.data_df = data_df
        self.data_df.reset_index(drop=True, inplace=True)   
    #     self.clean_stale_snapshots()

    def has_new_data(self) -> bool:
        prev_snapshot_df = self._load_snapshot_df()
        prev_snapshot_df.reset_index(drop=True, inplace=True)

        # No prior data.
        if prev_snapshot_df.empty:
            print("No previous snapshot; writing data to file.")
            self._write_snapshot_df()
            return True

        # No changes.
        if prev_snapshot_df.equals(self.data_df):
            print("No changes in data from snapshot.")
            return False

        # There are diffs in the snapshots.
        # V2: Determine whether it's a notification-worthy change: New tee-time added.   
        print("Diffs in snapshots.")
        has_notable_diffs = self._compare_snapshot_df(prev_snapshot_df)        

        # self._clear_snapshots_dir()
        # self._write_snapshot_df()

        return True

    def _load_snapshot_df(self) -> pd.DataFrame:
        for _, _, files in os.walk(SNAPSHOTS_DIR):
            for file_name in files:
                if 'pickle' in file_name:
                    print("Loading {file_name} into DataFrame".format(file_name=file_name))
                    return pd.read_pickle(os.path.join(SNAPSHOTS_DIR, file_name))
        return pd.DataFrame()

    def _compare_snapshot_df(self, prev_snapshot_df: pd.DataFrame) -> bool:
        print("\nprev_snapshot_df")
        print(prev_snapshot_df)
        print("\ndata_df")
        print(self.data_df)


        diff_df = pd.concat([prev_snapshot_df, self.data_df]).drop_duplicates(keep=False)
        print("\ndiff_df")
        print(diff_df)

        merged_df = pd.merge(diff_df, prev_snapshot_df, how='left', indicator='Exists')
        print("\nmerged_df")
        print(merged_df)
        # merged_df['Exist'] = np.where(merged_df['Exist'] == 'both', True, False)
        # print(merged_df)

        # for row in diff_df.iterrows():
        #     # If row was NOT in prev snapshot, this is a new addition to report.
        #     if row not in prev_snapshot_df:
        #         print("Not in prev snapshot:", row)
        #         return True
        return False


        print(self.data_df.compare(prev_snapshot_df))

    def _write_snapshot_df(self) -> None:
        timestamp = dt.datetime.now()
        pickle_path = os.path.join(SNAPSHOTS_DIR, '{timestamp}.pickle'.format(timestamp=timestamp))
        csv_path = os.path.join(SNAPSHOTS_DIR, '{timestamp}.csv'.format(timestamp=timestamp))
        with open(pickle_path, 'wb') as f:
            pickle.dump(self.data_df, f)
            print("Pickled data into {path}...".format(path=pickle_path))
        self.data_df.to_csv(csv_path)
        print("Dumped data into {path}...".format(path=csv_path))

    def _clear_snapshots_dir(self) -> None:
        print("Deleting", SNAPSHOTS_DIR)
        rmtree(SNAPSHOTS_DIR)

    # def clean_stale_snapshots(self) -> None:
    #     if os.path.exists(TMP_SUBDIR):
    #         rmtree(TMP_SUBDIR)

    #     today = dt.date.today()
    #     for _, _, json_files in os.walk(SNAPSHOTS_DIR):
    #         for f in json_files:
    #             file_path = os.path.join(SNAPSHOTS_DIR, f)
    #             snapshot_date = dt.datetime.strptime(f.replace('.json', ''), "%Y%m%d")
    #             # Delete directories of dates that already passed
    #             if snapshot_date.date() < today:
    #                 print("Deleting", file_path)
    #                 rmtree(file_path)

    # def snapshot_results(self, is_tmp=True) -> None:
    #     for date, results in self.aggregated_results.items():
    #         json_data = self._convert_to_json_data(results)
    #         dir_path = TMP_SUBDIR if is_tmp else SNAPSHOTS_DIR 
    #         self._write_json_to_file(dir_path=dir_path, target_date=date, json_data=json_data)


    # # Maybe the better way to handle snapshots is to just snapshot the content sent for notification
    # # and compare with that. Rather than comparing with the previous run.
    # def diff_snapshots(self) -> None:
    #     for _, _, tmp_files in os.walk(TMP_SUBDIR):
    #         print(tmp_files)
    #         for file_name in tmp_files:
    #             tmp_snapshot = os.path.join(TMP_SUBDIR, file_name)
    #             prev_snapshot = os.path.join(SNAPSHOTS_DIR, file_name)
    #             if self._has_diffs(path1=tmp_snapshot, path2=prev_snapshot):
    #                 print("{0} has diffs!".format(file_name))

    #             else:
    #                 print("{0} and {1} are the same.".format(tmp_snapshot, prev_snapshot))


    # def _extract_diffs(self, path1: str, path2: str) -> str:
    #     pass

    # def _has_diffs(self, path1: str, path2: str) -> bool:
    #     return not filecmp.cmp(path1, path2)


    # def _write_json_to_file(self, dir_path: str,
    #                               target_date: dt.date, 
    #                               json_data: Dict[str, List[str]]) -> None:
    #     if not os.path.exists(dir_path):
    #         print("Initializing", dir_path)
    #         os.mkdir(dir_path)

    #     snapshot_path = self._build_snapshot_path(dir_path=dir_path, target_date=target_date)
    #     with open(snapshot_path, 'w') as f:
    #         f.write(json.dumps(json_data, indent=2))
    #         print("Snapshot written to", snapshot_path)

    # def _convert_to_json_data(
    #     self, results: List[Tuple[GolfCourse, List[dt.date]]]) -> Dict[str, List[str]]:
    #     json_data = OrderedDict()
    #     sorted_results = sorted(results)
    #     for course, tee_times in sorted_results:
    #         json_data[course.tag] = [ t.strftime("%H:%M") for t in tee_times ]
    #     return json_data

    # def _build_snapshot_path(self, dir_path: str, target_date: dt.date):
    #     return os.path.join(dir_path, "{date}.json".format(date=target_date.strftime("%Y%m%d")))



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




