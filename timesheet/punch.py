import os
import sys
import pandas as pd

class Timesheet:

    def __init__(self, sheet):

        path_here = os.path.abspath(os.path.dirname(__file__))
        self._timesheet_path = os.path.join(path_here, sheet)

        if os.path.isfile(self._timesheet_path):
            self._timesheet = pd.read_csv(self._timesheet_path, sep="\t", parse_dates=["time"])
        else:
            print(f"Existing timesheet not found. Creating new timesheet at '{self._timesheet_path}'.")
            self._timesheet = pd.DataFrame()

    def _get_weeks_table(self):

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
        groupby([pd.Grouper(key="punch", freq="W-SUN")])["time"].\
        sum()

        return net

    def _summarize_weeks(self):

        net = self._get_weeks_table().\
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


if len(sys.argv) < 3:
    raise ValueError("Insufficient number of arguments passed. Please specify 'in' or 'out' and 'b' or 'p'.")

if len(sys.argv) in (3, 5, 8):

    if sys.argv[1] in ("in", "out", "check", "summarize"):
        if sys.argv[-1] in ("b", "p"):
            ts = Timesheet("bundy202201.tsv" if sys.argv[-1] == "b" else "payne202201.tsv")

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
                time = pd.Timestamp(now.year, now.month, now.day, *[int(i) for i in sys.argv[2:-1]])
                ts.punch(io=sys.argv[1], time=time)        
            else:
                punch_time_list = [int(i) for i in sys.argv[2:-1]]
                time = pd.Timestamp(*punch_time_list)
                ts.punch(io=sys.argv[1], time=time)
        else:
            raise ValueError(f"Invalid sheet. You passed '{sys.argv[-1]}'. Please pass 'b' for Bundy Lab or 'p' for Payne Lab.")
    else:
        raise ValueError(f"Invalid punch type. You passed '{sys.argv[1]}'. Please pass 'in' or 'out'.")
else:
    raise ValueError(f"Wrong number of arguments. You passed {len(sys.argv) - 1} arguments. Pass either two ('in' or 'out' and 'b' or 'p') or six ('in' or 'out' and year, month, day, 24 hour, minute) and 'b' or 'p'.")
