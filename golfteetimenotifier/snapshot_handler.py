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
import pickle


PROJECT_DIR = "golfteetimenotifier/"
SNAPSHOTS_DIR = os.path.abspath(
    "{0}output/snapshots".format(PROJECT_DIR if PROJECT_DIR not in os.getcwd() else ""))
SNAPSHOT_PICKLE = os.path.join(SNAPSHOTS_DIR, "snapshot.pickle")
SNAPSHOT_CSV = os.path.join(SNAPSHOTS_DIR, "snapshot.csv")


class SnapshotHandler():
    def __init__(self, data_df: pd.DataFrame) -> None:
        self.curr_snapshot_df = data_df
        self.curr_snapshot_df.reset_index(drop=True, inplace=True)  
        self.prev_snapshot_df = self._load_snapshot_df()

    def has_new_tee_times(self) -> bool:
        # No prior data.
        if self.prev_snapshot_df == None:
            print("No previous snapshot; writing data to file.")
            self._write_snapshot_df()
            return True

        # No changes.
        if self.prev_snapshot_df.equals(self.curr_snapshot_df):
            print("No changes in data from snapshot.")
            return False

        # There are diffs in the snapshots.
        has_new_tee_times = self._has_new_tee_times()        
        print("Diffs in snapshots -> new tee times? ", has_new_tee_times)

        self._clear_snapshots_dir()
        self._write_snapshot_df()
        return has_new_tee_times

    def _load_snapshot_df(self) -> pd.DataFrame:
        if os.path.exists(SNAPSHOT_PICKLE):
            print("Loading {file_name} into DataFrame".format(file_name=SNAPSHOT_PICKLE))
            df = pd.read_pickle(SNAPSHOT_PICKLE)
            df.reset_index(drop=True, inplace=True) 
            return df
        print(SNAPSHOT_PICKLE, "does not exist.")
        return None

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
        if not os.path.exists(SNAPSHOTS_DIR):
            print("Initializing", SNAPSHOTS_DIR)
            os.makedirs(SNAPSHOTS_DIR)

        with open(SNAPSHOT_PICKLE, 'wb+') as f:
            pickle.dump(self.curr_snapshot_df, f)
            print("Pickled data into {path}...".format(path=SNAPSHOT_PICKLE))
        self.curr_snapshot_df.to_csv(SNAPSHOT_CSV)
        print("Dumped data into {path}...".format(path=SNAPSHOT_CSV))

    def _clear_snapshots_dir(self) -> None:
        print("Deleting", SNAPSHOTS_DIR)
        rmtree(SNAPSHOTS_DIR)
