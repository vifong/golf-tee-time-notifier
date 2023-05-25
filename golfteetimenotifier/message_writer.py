from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
import datetime as dt
import pandas as pd

MESSAGE_OUTPUT_FILE = "output/message.txt"


class NotificationMessageWriter():
    def __init__(self, data_df: pd.DataFrame) -> None:
        self.grouped_df = data_df.groupby(['Course', 'Date'])['Tee Time'].apply(list)
        print(grouped_df)

    def write(self) -> str:
        message = self._craft()
        with open(MESSAGE_OUTPUT_FILE, 'w') as f:
            f.write(message)
            print("Message written to", MESSAGE_OUTPUT_FILE)

    def _craft(self) -> str:
        message = "***Tee Times Alert!***\n"

        grouped_df = data_df.groupby(['Course', 'Date'])



        for course_name, tee_times in self.results.items():
            message += "\n{course}\n".format(course=self._format_course_name(course_name))
            for date, times in tee_times:
                message += "{date} {times}\n".format(
                    date=self._format_date(date), times=self._format_times(times))

        print(message)
        return message

    def _sort_df(self) -> None:
        # self.data_df.sort_values(['Course', 'Date', 'Tee Time'])
        print(self.data_df.group_by(['Course', 'Date']))

    def _format_date(self, date: dt.date) -> str:
        return date.strftime("%a, %b %d") 

    def _format_course_name(self, course_name) -> str:
        return course_name.replace(" Golf Course", '').upper()

    def _format_times(self, times: List[dt.date]) -> str:
        formatted_times = []
        for t in times:
            formatted_time = t.strftime("%I:%M%p")
            if formatted_time[0] == '0':
                formatted_time = formatted_time[0:]
            formatted_times.append(formatted_time)

        return str(formatted_times).replace(' ', '')
