import os
import sys
import pandas as pd

class Timesheet:

    def __init__(self):

        path_here = os.path.abspath(os.path.dirname(__file__))
        self._timesheet_path = os.path.join(path_here, "timesheet.tsv")

        if os.path.isfile(self._timesheet_path):
            self._timesheet = pd.read_csv(self._timesheet_path, sep="\t", parse_dates=["time"])
        else:
            print(f"Existing timesheet not found. Creating new timesheet at '{self._timesheet_path}'.")
            self._timesheet = pd.DataFrame()

    def _summarize_week(self):
        return self._timesheet

    def _summarize_all(self):

        ins, outs = self._get_ins_outs()

        # If we're currently clocked in, summarize time worked until now
        if self._timesheet.iloc[-1, 0] == "in":
            outs = outs.append({"io": "out", "time": pd.Timestamp.now()}, ignore_index=True)

        # Index by punch in time
        ins.index = ins["time"]
        ins.index.name = "punch"

        outs.index = ins["time"]
        outs.index.name = "punch"

        # Sum by week
        net = (outs["time"] - ins["time"]).\
        reset_index().\
        groupby([pd.Grouper(key="punch", freq="W-MON")])["time"].\
        sum().\
        apply(self._fmt_timedelta)

        # Offset week
        net.index = net.index - pd.to_timedelta(7, unit="d")

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

        tmp = self._timesheet.append({
            "time": time,
            "io": io
        },
        ignore_index=True)

        if tmp.duplicated().any():
            raise ValueError(f"Invalid punch. Creates duplicate row.")

        self._timesheet = tmp.sort_values(by="time").reset_index(drop=True)
        self._check_matches()
        print(self._summarize_all().iloc[-1])
        self._save()

    def check(self):
        print(self._summarize_all().iloc[-1])

if len(sys.argv) < 2:
    raise ValueError("Insufficient number of arguments passed. Please specify 'in' or 'out'.")

if len(sys.argv) in (2, 7):

    if sys.argv[1] in ("in", "out", "check"):
        ts = Timesheet()

        if sys.argv[1] == "check":
            if len(sys.argv) > 2:
                print("Note: Ignoring extra args after 'check'")
            ts.check()
        elif len(sys.argv) == 2:
            ts.punch(io=sys.argv[1])
        else:
            punch_time_list = [int(i) for i in sys.argv[2:]]
            time = pd.Timestamp(*punch_time_list)
            ts.punch(io=sys.argv[1], time=time)
    else:
        raise ValueError(f"Invalid punch type. You passed '{sys.argv[1]}'. Please pass 'in' or 'out'.")
else:
    raise ValueError(f"Wrong number of arguments. You passed {len(sys.argv) - 1} arguments. Pass either one ('in' or 'out') or six ('in' or 'out' and year, month, day, 24 hour, minute).")
