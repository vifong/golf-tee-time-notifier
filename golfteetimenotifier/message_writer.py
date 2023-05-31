from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
import datetime as dt
import os
import pandas as pd


MESSAGE_OUTPUT_FILE = "message.txt"


class NotificationMessageWriter():
    def __init__(self, data_df: pd.DataFrame) -> None:
        self.data_df = data_df

    def write(self) -> str:
        message = self._craft()
        with open(MESSAGE_OUTPUT_FILE, 'w') as f:
            f.write(message)
            print("Message written to", MESSAGE_OUTPUT_FILE)
            f.close()

    def delete(self) -> None:
        if not os.path.exists(MESSAGE_OUTPUT_FILE):
            print(MESSAGE_OUTPUT_FILE, "does not exist.")
        try:
            os.remove(MESSAGE_OUTPUT_FILE)
            print("Deleted ", MESSAGE_OUTPUT_FILE)
        except:
            print("Failed to delete", MESSAGE_OUTPUT_FILE) 

    def _craft(self) -> str:
        grouped_df = self.data_df.groupby(['Course', 'Date'])['Tee Time'].apply(list)
        print(grouped_df)

        message = "***Tee Times Alert!***\n"
        curr_course = ""
        for (course_name, date), tee_times in grouped_df.items():
            if course_name != curr_course:
                message += "\n{course}\n".format(course=self._format_course_name(course_name))
                curr_course = course_name
            message += "{date} {times}\n".format(
                date=self._format_date(date), times=self._format_times(tee_times))

        message += "\nhttps://golf.lacity.org/"
        print("\n==Message==\n", message)
        return message

    def _format_date(self, date: dt.date) -> str:
        return date.strftime("%a, %b %d") 

    def _format_course_name(self, course_name) -> str:
        return course_name.replace(" Golf Course", '').upper()

    def _format_times(self, times: List[dt.date]) -> str:
        formatted_times = []
        for t in times:
            formatted_time = t.strftime("%I:%M%p")
            if formatted_time[0] == '0':
                formatted_time = formatted_time[1:]
            formatted_times.append(formatted_time)

        return str(formatted_times).replace('\'', '').replace(' ', '')
