from dateutil.parser import parse
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import math

def get_bedtime_start_date(cycle_start_time: str) -> datetime.datetime:
  """Returns a datetime that has the day, but not time, that the sleep began.

  Args:
    sleep_onset: This should be the Whoop 'Cycle start time' value for this row as a string.
  """
  cycle_st = parse(cycle_start_time)
  if cycle_st.hour < 8:
    cycle_st = cycle_st - relativedelta(days=1)
  cycle_st = cycle_st.replace(hour=0, minute=0, second=0, microsecond=0)
  return cycle_st

def convert_to_hours(minutes: float) -> str:
  if math.isnan(minutes):
    return "-"
  hours = minutes // 60
  minutes_remaining = minutes - (60 * hours)
  return f"{round(hours)}:{round(minutes_remaining):02}"
  
whoop_directory = './my_whoop_data_2024_08_27/'
sleeps_file = whoop_directory + 'sleeps.csv'
whoop = pd.read_csv(sleeps_file)
whoop = whoop[whoop['Nap'] == False]
naps = whoop[whoop['Nap'] == True]
whoop['Cycle start time'] = whoop['Cycle start time'].map(get_bedtime_start_date)
whoop = whoop.rename(columns={'Cycle start time': 'Day'})
whoop.set_index('Day', inplace=True)

#minute_columns = ['Asleep duration (min)', 'Deep (SWS) duration (min)', 'REM duration (min)', 'Sleep need (min)']
#for minute_column in minute_columns:
#  df[minute_column] = df[minute_column].map(convert_to_hours)

#desired_columns = ['Cycle start time', 'Asleep duration (min)', 'Deep (SWS) duration (min)', 'REM duration (min)', 'Respiratory rate (rpm)', 'Sleep need (min)', 'Sleep performance %']
#df = df.filter(items=desired_columns)
#df = df.reindex(desired_columns, axis=1)
#df = df.rename(columns={'Cycle start time': 'Date', 'Deep (SWS) duration (min)': 'SWS', 'Asleep duration (min)': 'Asleep', 'REM duration (min)': 'REM'})

cronometer_servings = 'servings.csv'
cronometer_summary = 'dailysummary.csv'

cm = pd.read_csv(cronometer_servings)
cm['Day'] = cm['Day'].map(lambda day: parse(day))
cm.set_index('Day', inplace=True)

merged = pd.concat([cm, whoop])

with open('output.csv', 'w') as f:
  f.write(merged.to_csv())
print(merged.to_string(index=False))