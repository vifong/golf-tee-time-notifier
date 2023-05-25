from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
import datetime


MESSAGE_OUTPUT_FILE = "output/message.txt"


class NotificationMessageWriter():
    def __init__(self, results: Dict[str, List[Tuple[datetime.date, List[datetime.date]]]], 
                       output_file: str) -> None:
        # key: course name
        # value: [(date, [times]), ...]
        self.results = results
        self.output_file = output_file

    def write(self) -> str:
        message = self._craft()
        with open(self.output_file, 'w') as f:
            f.write(message)
            print("Message written to", self.output_file)

    def _craft(self) -> str:
        message = "***Tee Times Alert!***\n"
        for course_name, tee_times in self.results.items():
            message += "\n{course}\n".format(course=self._format_course_name(course_name))
            for date, times in tee_times:
                message += "{date} {times}\n".format(
                    date=self._format_date(date), times=self._format_times(times))

        print(message)
        return message

    def _format_date(self, date: datetime.date) -> str:
        return date.strftime("%a, %b %d") 

    def _format_course_name(self, course_name) -> str:
        return course_name.replace(" Golf Course", '').upper()

    def _format_times(self, times: List[datetime.date]) -> str:
        formatted_times = []
        for t in times:
            formatted_time = t.strftime("%I:%M%p")
            if formatted_time[0] == '0':
                formatted_time = formatted_time[0:]
            formatted_times.append(formatted_time)

        return str(formatted_times).replace(' ', '')
