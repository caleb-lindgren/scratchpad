import os
import sys
import pandas as pd

class Timesheet:

    def __init__(self, timesheet_path="timesheet.tsv"):

        self._timesheet_path = os.path.abspath(timesheet_path)

        if os.path.isfile(self._timesheet_path):
            self.timesheet = pd.read_csv(self._timesheet_path, sep="\t")
        else:
            print(f"Existing timesheet not found. Creating new timesheet at '{self._timesheet_path}'.")
            self.timesheet = pd.DataFrame()

    def summarize_week(self):
        return self.timesheet

    def summarize_all(self):
        pass

    def punch(self, io, time=pd.Timestamp.now()):

        self.timesheet.append({
            "time": time,
            "io": io
        })

        print(self.summarize_week)

    def save(self):
        self.timesheet.to_csv(self._timesheet_path, sep="\t"), index=False)
        print(f"Timesheet saved to '{self._timesheet_path}'.")


if len(sys.argv < 2):
    raise ValueError("Insufficient number of arguments passed. Please specify 'in' or 'out'.")

if len(sys.argv == 2):

    if sys.argv[1] in ("in", "out"):
        ts = Timesheet()
        ts.punch(io=sys.argv[1])
        ts.save()

    else:
        raise ValueError(f"Invalid punch type. You passed '{sys.argv[1]}'. Please pass 'in' or 'out'.")

elif len(sys.argv == 7):

    if sys.argv[1] in ("in", "out"):
        ts = Timesheet()
        ts.punch(io=sys.argv[1])
        ts.save()

    else:
        raise ValueError(f"Invalid punch type. You passed '{sys.argv[1]}'. Please pass 'in' or 'out'.")

else:
    raise ValueError(f"Too many arguments. You passed {len(sys.argv) - 1} arguments. Pass either one ('in' or 'out') or six ('in' or 'out' and year, month, day, 24 hour, minute).")
