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


class SnapshotHandler():
    SNAPSHOT_PICKLE = "snapshot.pickle"
    SNAPSHOT_CSV = "snapshot.csv"

    def __init__(self, data_df: pd.DataFrame) -> None:
        self.curr_snapshot_df = data_df
        self.curr_snapshot_df.reset_index(drop=True, inplace=True)  
        self.prev_snapshot_df = self.load_snapshot_df()
        self.prev_snapshot_df.reset_index(drop=True, inplace=True)

        print("\n==PREVIOUS SNAPSHOT==", self.prev_snapshot_df)
        print("\n==CURRENT SNAPSHOT==", self.curr_snapshot_df)

    def load_snapshot_df(self) -> pd.DataFrame:
        if os.path.exists(self.SNAPSHOT_PICKLE):
            print("Loading {file_name} into DataFrame...".format(file_name=self.SNAPSHOT_PICKLE))
            return pd.read_pickle(self.SNAPSHOT_PICKLE)
        print(self.SNAPSHOT_PICKLE, "does not exist.")
        return pd.DataFrame()

    def write_snapshot_df(self) -> None:
        with open(self.SNAPSHOT_PICKLE, 'wb+') as f:
            pickle.dump(self.curr_snapshot_df, f)
            print("Pickled data into {path}...".format(path=self.SNAPSHOT_PICKLE))
        self.curr_snapshot_df.to_csv(self.SNAPSHOT_CSV)
        print("Dumped data into {path}...".format(path=self.SNAPSHOT_CSV))

    def has_new_tee_times(self) -> bool:
        # No current data.
        if self.curr_snapshot_df.empty:
            print("No current data.")
            return False

        # No prior data.
        if self.prev_snapshot_df.empty:
            print("No previous snapshot.")
            return True

        # No changes.
        if self.prev_snapshot_df.equals(self.curr_snapshot_df):
            print("No changes in data from snapshot.")
            return False

        # There are diffs in the snapshots.
        has_new_tee_times = self._has_new_tee_times()        
        print("Diffs in snapshots -> new tee times? ", has_new_tee_times)
        return has_new_tee_times

    def _has_new_tee_times(self) -> bool:
        merged_df = pd.merge(self.prev_snapshot_df, self.curr_snapshot_df, 
                             how='right', indicator='Exists')
        print("\nmerged_df:\n", merged_df)

        # Return True iff there are new tee times from the current snapshot that was not in the 
        # previous snapshot
        return 'right_only' in set(merged_df['Exists'])
