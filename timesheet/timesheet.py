import os
import sys
import pandas as pd

class Timesheet:

    def __init__(self, timesheet_path="timesheet.tsv"):

        self._timesheet_path = os.path.abspath(timesheet_path)

        if os.path.isfile(self._timesheet_path):
            self.timesheet = pd.read_csv(self._timesheet_path, sep="\t", parse_dates=["time"])
        else:
            print(f"Existing timesheet not found. Creating new timesheet at '{self._timesheet_path}'.")
            self.timesheet = pd.DataFrame()

    def summarize_week(self):
        return self.timesheet

    def summarize_all(self):
        pass

    def punch(self, io, time=pd.Timestamp.now()):

        tmp = self.timesheet.append({
            "time": time,
            "io": io
        },
        ignore_index=True)

        if tmp.duplicated().any():
            raise ValueError(f"Invalid punch. Creates duplicate row.")

        self.timesheet = tmp.sort_values(by="time").reset_index(drop=True)

        print(self.summarize_week())

    def save(self):
        self.timesheet.to_csv(self._timesheet_path, sep="\t", index=False)
        print(f"Timesheet saved to '{self._timesheet_path}'.")


if len(sys.argv) < 2:
    raise ValueError("Insufficient number of arguments passed. Please specify 'in' or 'out'.")

if len(sys.argv) in (2, 7):

    if sys.argv[1] in ("in", "out"):
        ts = Timesheet()

        if len(sys.argv) == 2:
            ts.punch(io=sys.argv[1])
        else:
            punch_time_list = [int(i) for i in sys.argv[2:]]
            time = pd.Timestamp(*punch_time_list)
            ts.punch(io=sys.argv[1], time=time)

        ts.save()

    else:
        raise ValueError(f"Invalid punch type. You passed '{sys.argv[1]}'. Please pass 'in' or 'out'.")

else:
    raise ValueError(f"Wrong number of arguments. You passed {len(sys.argv) - 1} arguments. Pass either one ('in' or 'out') or six ('in' or 'out' and year, month, day, 24 hour, minute).")
