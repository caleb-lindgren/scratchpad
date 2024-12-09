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

	def _get_time_deltas(self, prefix):

		ins, outs = self._get_ins_outs(prefix)

		# If we're currently clocked in, summarize time worked until now
		if self._timesheet.iloc[-1, 0] == f"{prefix}in":
			outs = pd.concat([outs, pd.DataFrame({
				"io": [f"{prefix}out"],
				"time": [pd.Timestamp.now()],
			})], ignore_index=True)

		# Index by punch in time
		ins.index = ins["time"]
		ins.index.name = "punch"

		outs.index = ins["time"]
		outs.index.name = "punch"

		# Get deltas
		deltas = (outs["time"] - ins["time"]).reset_index()

		return deltas

	def _group_time_deltas(self, deltas):

		# Sum by week
		net = deltas.\
		groupby([pd.Grouper(key="punch", freq="W-FRI")])["time"].\
		sum()

		return net

	def _get_weeks_table(self, prefix):

		deltas = self._get_time_deltas(prefix)
		net = self._group_time_deltas(deltas)

		return net

	def _get_combined_weeks_table(self):

		deltas = self._get_time_deltas(prefix="")
		vdeltas = self._get_time_deltas(prefix="v")

		comb = pd.concat([deltas, vdeltas], ignore_index=True)
		net = self._group_time_deltas(comb)

		return net

	def _summarize_weeks(self, prefix):

		net = self._get_weeks_table(prefix).\
		apply(self._fmt_timedelta)

		# Offset week
		net.index = net.index - pd.to_timedelta(6, unit="d")

		return net

	def _fmt_timedelta(self, tdelta):
		total_secs = abs(tdelta.total_seconds())
		hrs = int(total_secs / 3600)
		min = int(total_secs % 3600 / 60)
		sec = int(total_secs % 3600 % 60)
		return f"{'-' if tdelta.total_seconds() < 0 else ''}{hrs:02d}:{min:02d}:{sec:02d}"

	def _get_ins_outs(self, prefix):

		self._timesheet = self.\
		_timesheet.\
		sort_values(by="time").\
		reset_index(drop=True)

		ins = self._timesheet[self._timesheet["io"] == f"{prefix}in"]
		outs = self._timesheet[self._timesheet["io"] == f"{prefix}out"]

		return ins, outs

	def _check_matches(self, prefix):

		ins, outs = self._get_ins_outs(prefix)

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
		self._check_matches("")
		self._check_matches("v")
		self.check_current()
		self._save()

	def check_current(self):
		print(self._summarize_weeks("").iloc[-1])

	def summarize_all(self):
		weeks = self._summarize_weeks("")
		weeks.index.name = None
		print(weeks, end="\r")
		print(" " * 30)

		#print("Vacation:")
		#vweeks = self._summarize_weeks("v")
		#vweeks.index.name = None
		#print(vweeks, end="\r")
		#print(" " * 30)

		weeks_table = self._get_weeks_table("")
		vweeks_table = self._get_weeks_table("v")
		comb_table = self._get_combined_weeks_table()

		net = weeks_table.sum()
		print(f"Total: {self._fmt_timedelta(net)}")

		vnet = vweeks_table.sum()
		print(f"Vacation total: {self._fmt_timedelta(vnet)}")

		mean = comb_table.iloc[:-1].mean()
		print(f"Weekly mean: {self._fmt_timedelta(mean)}")

		diff = comb_table.iloc[:-1].sum() - (pd.Timedelta("40 hours") * (comb_table.shape[0] - 1))
		print(f"Total lack/excess: {self._fmt_timedelta(diff)}")

if len(sys.argv) < 3:
	raise ValueError("Insufficient number of arguments passed. Please specify 'in', 'out', 'vin', 'vout', 'check', or 'summarize' and a path to a timesheet tsv file.")

if len(sys.argv) in (3, 5, 8):

	if sys.argv[1] in ("in", "out", "vin", "vout", "check", "summarize"):

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
		raise ValueError(f"Invalid punch type. You passed '{sys.argv[1]}'. Please pass 'in', 'out', 'vin', 'vout', 'check', or 'summarize'.")
else:
	raise ValueError(f"Wrong number of arguments. You passed {len(sys.argv) - 1} arguments. Pass either two ('in', 'out', 'vin', 'vout', 'check', or 'summarize' and a path to a timesheet tsv file) or six ('in' or 'out', a path to a timesheet tsv file, and year, month, day, 24 hour, minute).")
