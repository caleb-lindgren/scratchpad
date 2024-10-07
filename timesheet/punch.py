import os
import sys
import pandas as pd

class Timesheet:

    def __init__(self, timesheet_path):

        self._timesheet_path = timesheet_path

        if os.path.isfile(self._timesheet_path):
            self._timesheet = pd.read_csv(self._timesheet_path, sep="\t", parse_dates=["time"])
        else:
            resp = input(f"Existing timesheet not found. Did you mistype the path? If not, and you would like to create a new timesheet at '{self._timesheet_path}', enter 'y'. Otherwise enter 'n': ")

            while resp not in ("y", "n"):
                resp = input("Invalid response. Please enter 'y' or 'n': ")

            if resp == "y":
                print(f"Creating new timesheet at '{self._timesheet_path}'.")
                self._timesheet = pd.DataFrame()
            elif resp == "n":
                sys.exit()

    def _get_weeks_table(self):

        ins, outs = self._get_ins_outs()

        # If we're currently clocked in, summarize time worked until now
        if self._timesheet.iloc[-1, 0] == "in":
            outs = pd.concat([outs, pd.DataFrame({
                "io": ["out"],
                "time": [pd.Timestamp.now()],
            })], ignore_index=True)

        # Index by punch in time
        ins.index = ins["time"]
        ins.index.name = "punch"

        outs.index = ins["time"]
        outs.index.name = "punch"

        # Sum by week
        net = (outs["time"] - ins["time"]).\
        reset_index().\
        groupby([pd.Grouper(key="punch", freq="W-FRI")])["time"].\
        sum()

        return net

    def _summarize_weeks(self):

        net = self._get_weeks_table().\
        apply(self._fmt_timedelta)

        # Offset week
        net.index = net.index - pd.to_timedelta(6, unit="d")

        return net

    def _fmt_timedelta(self, tdelta):
        day_hrs = tdelta.days * 24
        hrs, rem = divmod(tdelta.seconds, 3600)
        min, sec = divmod(rem, 60)

        hrs = hrs + day_hrs
        return f"{hrs:02d}:{min:02d}:{sec:02d}"

    def _get_ins_outs(self):

        self._timesheet = self.\
        _timesheet.\
        sort_values(by="time").\
        reset_index(drop=True)

        ins = self._timesheet[self._timesheet["io"] == "in"]
        outs = self._timesheet[self._timesheet["io"] == "out"]

        return ins, outs

    def _check_matches(self):

        ins, outs = self._get_ins_outs()

        if (ins.index % 2 != 0).any() or (outs.index % 2 == 0).any():
            raise ValueError(f"Punch mismatch:\n{self._timesheet.tail()}")

    def _save(self):
        self._timesheet.to_csv(self._timesheet_path, sep="\t", index=False)

    def punch(self, io, time=pd.Timestamp.now()):

        tmp = pd.concat([self._timesheet, pd.DataFrame({
            "io": [io],
            "time": [time],
        })],
        ignore_index=True)

        if tmp.duplicated().any():
            raise ValueError(f"Invalid punch. Creates duplicate row.")

        self._timesheet = tmp.sort_values(by="time").reset_index(drop=True)
        self._check_matches()
        self.check_current()
        self._save()

    def check_current(self):
        print(self._summarize_weeks().iloc[-1])

    def summarize_all(self):
        weeks = self._summarize_weeks()
        weeks.index.name = None
        print(weeks, end="\r")
        print(" " * 30)

        net = self._get_weeks_table().sum()
        print(f"Total: {self._fmt_timedelta(net)}")

        mean = self._get_weeks_table().iloc[:-1].mean()
        print(f"Mean: {self._fmt_timedelta(mean)}")

if len(sys.argv) < 3:
    raise ValueError("Insufficient number of arguments passed. Please specify 'in', 'out', 'check', or 'summarize' and a path to a timesheet tsv file.")

if len(sys.argv) in (3, 5, 8):

    if sys.argv[1] in ("in", "out", "check", "summarize"):

        ts = Timesheet(sys.argv[2])

        if sys.argv[1] == "check":
            if len(sys.argv) > 3:
                print("Note: Ignoring extra args after 'check'")
            ts.check_current()
        elif sys.argv[1] == "summarize":
            if len(sys.argv) > 3:
                print("Note: Ignoring extra args after 'summarize'")
            ts.summarize_all()
        elif len(sys.argv) == 3:
            ts.punch(io=sys.argv[1])
        elif len(sys.argv) == 5:
            now = pd.Timestamp.now()
            time = pd.Timestamp(now.year, now.month, now.day, *[int(i) for i in sys.argv[3:]])
            ts.punch(io=sys.argv[1], time=time)        
        else:
            punch_time_list = [int(i) for i in sys.argv[3:]]
            time = pd.Timestamp(*punch_time_list)
            ts.punch(io=sys.argv[1], time=time)
    else:
        raise ValueError(f"Invalid punch type. You passed '{sys.argv[1]}'. Please pass 'in', 'out', 'check', or 'summarize'.")
else:
    raise ValueError(f"Wrong number of arguments. You passed {len(sys.argv) - 1} arguments. Pass either two ('in', 'out', 'check', or 'summarize' and a path to a timesheet tsv file) or six ('in' or 'out', a path to a timesheet tsv file, and year, month, day, 24 hour, minute).")
