from typing import List
import datetime as dt
import os
import pandas as pd


class NotificationMessageWriter():
    MESSAGE_OUTPUT_FILE = "message.txt"

    def __init__(self, data_df: pd.DataFrame) -> None:
        self.data_df = data_df

    def write(self) -> str:
        message = self._craft()
        with open(self.MESSAGE_OUTPUT_FILE, 'w') as f:
            f.write(message)
            print("Message written to", self.MESSAGE_OUTPUT_FILE)
            f.close()

    def delete(self) -> None:
        if not os.path.exists(self.MESSAGE_OUTPUT_FILE):
            print(self.MESSAGE_OUTPUT_FILE, "does not exist.")
        try:
            os.remove(self.MESSAGE_OUTPUT_FILE)
            print("Deleted", self.MESSAGE_OUTPUT_FILE)
        except:
            print("Failed to delete", self.MESSAGE_OUTPUT_FILE) 

    def _craft(self) -> str:
        grouped_df = self.data_df.groupby(['Course', 'Date'])[['Tee Time', 'Players']].apply(
            lambda x: x.values.tolist())
        print("\n==GROUPED DATA==\n", grouped_df)

        message = ""
        curr_course = ""
        for (course_name, date), times_and_players in grouped_df.items():
            if course_name != curr_course:
                message += "\n{course}\n".format(course=self._format_course_name(course_name))
                curr_course = course_name
            message += "{date} {times}\n".format(
                date=self._format_date(date), 
                times=self._format_times_and_players(times_and_players))

        print("\n==MESSAGE==\n", message)
        return message

    def _format_date(self, date: dt.date) -> str:
        return date.strftime("%a, %b %d") 

    def _format_course_name(self, course_name) -> str:
        return course_name.replace(" Golf Course", '').upper()

    def _format_times_and_players(self, times_and_players: List[List]) -> str:
        formatted_tee_times = []
        for tp in times_and_players:
            formatted_pair = "{time}({players})".format(
                time=self._format_time(tp[0]), players=tp[1])
            formatted_tee_times.append(formatted_pair)
        return str(formatted_tee_times).replace('\'', '')

    def _format_time(self, time: dt.time) -> str:
        formatted_time = time.strftime("%I:%M%p")
        return formatted_time if formatted_time[0] != '0' else formatted_time[1:]
