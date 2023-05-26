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
        self.curr_snapshot_df = data_df
        self.prev_snapshot_df = self._load_snapshot_df()
        self.curr_snapshot_df.reset_index(drop=True, inplace=True)  
        self.prev_snapshot_df.reset_index(drop=True, inplace=True) 

    def has_new_tee_times(self) -> bool:
        # No prior data.
        if self.prev_snapshot_df.empty:
            print("No previous snapshot; writing data to file.")
            self._write_snapshot_df()
            return True

        # No changes.
        if self.prev_snapshot_df.equals(self.data_df):
            print("No changes in data from snapshot.")
            return False

        # There are diffs in the snapshots.
        has_new_tee_times = self._has_new_tee_times()        
        print("Diffs in snapshots -> new tee times? ", has_new_tee_times)

        self._clear_snapshots_dir()
        self._write_snapshot_df()
        return has_new_tee_times

    def _load_snapshot_df(self) -> pd.DataFrame:
        for _, _, files in os.walk(SNAPSHOTS_DIR):
            for file_name in files:
                if 'pickle' in file_name:
                    print("Loading {file_name} into DataFrame".format(file_name=file_name))
                    return pd.read_pickle(os.path.join(SNAPSHOTS_DIR, file_name))
        return pd.DataFrame()

    def _has_new_tee_times(self) -> bool:
        print("\nprev_snapshot_df:\n", self.prev_snapshot_df)
        print("\ncurr_snapshot_df:\n", self.curr_snapshot_df)

        merged_df = pd.merge(self.prev_snapshot_df, self.curr_snapshot_df, 
                             how='right', indicator='Exists')
        print("\nmerged_df:\n", merged_df)

        # Return True iff there are new tee times from the current snapshot that was not in the 
        # previous snapshot
        return 'right_only' in set(merged_df['Exists'])

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
