import pandas as pd

flie_list = ['Checkmarks.csv',
              'dailysummary.csv',
              'physiological_cycles.csv',
              'servings.csv',
              'sleeps.csv',
              'workouts.csv']
org_df_list = [pd.read_csv(x) for x in flie_list]



def prepare_slepps_df(tmp_df):
    tmp_df['Wake onset_new'] = pd.to_datetime(tmp_df['Wake onset'], format='%Y-%m-%d %H:%M:%S')
    tmp_df['Wake onset_new'] = pd.to_datetime(tmp_df['Wake onset']).dt.date
    tmp_df['Wake onset'] = tmp_df['Wake onset_new']
    tmp_df['Wake onset_new'] = pd.to_datetime(tmp_df['Wake onset']) - pd.Timedelta(days=1)
    tmp_df['Wake onset'] = pd.to_datetime(tmp_df['Wake onset'])
    tmp_df['Wake onset_new'] = pd.to_datetime(tmp_df['Wake onset_new'])
    tmp_df['Nap_shifted'] = tmp_df['Nap'].shift(-1)

    tmp_df[['Nap Asleep duration (min)', 'Nap In bed duration (min)', 'Nap Light sleep duration (min)',
            'Nap Deep (SWS) duration (min)', 'Nap REM duration (min)', 'Nap Awake duration (min)']] = 0

    def calculate_nap_values(row):
        if row['Nap_shifted'] == True:
            date_val_to_aggregate_on = row['Wake onset_new']
            row['Nap Asleep duration (min)'] = \
                tmp_df[(tmp_df['Wake onset'] == date_val_to_aggregate_on) & (tmp_df['Nap'] == True)][
                    'Asleep duration (min)'].sum()
            row['Nap In bed duration (min)'] = \
                tmp_df[(tmp_df['Wake onset'] == date_val_to_aggregate_on) & (tmp_df['Nap'] == True)][
                    'In bed duration (min)'].sum()
            row['Nap Light sleep duration (min)'] = \
                tmp_df[(tmp_df['Wake onset'] == date_val_to_aggregate_on) & (tmp_df['Nap'] == True)][
                    'Light sleep duration (min)'].sum()
            row['Nap Deep (SWS) duration (min)'] = \
                tmp_df[(tmp_df['Wake onset'] == date_val_to_aggregate_on) & (tmp_df['Nap'] == True)][
                    'Deep (SWS) duration (min)'].sum()
            row['Nap REM duration (min)'] = \
                tmp_df[(tmp_df['Wake onset'] == date_val_to_aggregate_on) & (tmp_df['Nap'] == True)][
                    'REM duration (min)'].sum()
            row['Nap Awake duration (min)'] = \
                tmp_df[(tmp_df['Wake onset'] == date_val_to_aggregate_on) & (tmp_df['Nap'] == True)][
                    'Awake duration (min)'].sum()
        return row

    tmp_df = tmp_df.apply(calculate_nap_values, axis=1)
    tmp_df['Wake onset'] = tmp_df['Wake onset_new']
    tmp_df = tmp_df.drop(columns=['Nap_shifted', 'Wake onset_new'])
    tmp_df.drop(tmp_df[tmp_df['Nap'] == True].index, inplace=True)
    return tmp_df


new_sleeps = prepare_slepps_df(org_df_list[flie_list.index('sleeps.csv')].copy())
# new_sleeps.to_csv('new_sleeps.csv')




def prepare_physic_df(tmp_df):
    tmp_df['Wake onset'] = pd.to_datetime(tmp_df['Wake onset'], format='%Y-%m-%d %H:%M:%S')
    tmp_df['Wake onset'] = tmp_df['Wake onset'].dt.date
    tmp_df['Wake onset'] = pd.to_datetime(tmp_df['Wake onset'])
    physiological_cols_to_be_shifted_prior_one_day = ['Recovery score %',
    'Resting heart rate (bpm)',
    'Heart rate variability (ms)',
    'Skin temp (celsius)',
    'Blood oxygen %']
    tmp_df[physiological_cols_to_be_shifted_prior_one_day] = tmp_df[physiological_cols_to_be_shifted_prior_one_day].shift(1)
    return tmp_df

new_physic = prepare_physic_df(org_df_list[flie_list.index('physiological_cycles.csv')].copy())
# new_physic.to_csv('new_physic.csv')




def prepare_foods_df(tmp_df):
    tmp_df['Day'] = pd.to_datetime(tmp_df['Day'], format='%Y-%m-%d')

    def process_value(value):
        value = value.strip()
        try:
            cleaned_value = ''.join(c for c in value if c.isdigit() or c == '.' or c.isspace())
            return float(cleaned_value)
        except ValueError:
            return value

    tmp_df['Amount'] = tmp_df['Amount'].apply(process_value)

    def aggregate_amount(values):
        numeric_values = []
        string_values = []

        for value in values:
            try:
                numeric_value = float(value)
                numeric_values.append(numeric_value)
            except ValueError:
                string_values.append(value)

        if numeric_values:
            numeric_sum = sum(numeric_values)
            if string_values:
                return f"{numeric_sum}, " + ', '.join(string_values)
            else:
                return numeric_sum
        else:
            return ', '.join(string_values)

    pivot_df = tmp_df.groupby(['Day', 'Food Name'])['Amount'].apply(aggregate_amount).reset_index()
    pivot_df = pivot_df.pivot(index='Day', columns='Food Name', values='Amount').reset_index()

    return pivot_df


food_df = prepare_foods_df(org_df_list[flie_list.index('servings.csv')].copy())
# food_df.to_csv('food.csv')

# checkmark_df
checkmark_df = org_df_list[flie_list.index('Checkmarks.csv')].copy()
checkmarks_column_to_be_merged = ['Date', 'Depression', 'Tiredness', 'Cronometer accurate?', 'Metta',
       'Concentration', 'Mouth tape', 'Wake early morning', 'Morning sunlamp',
       'Morning sun', 'Morning sun lux']

# dailysummary_df
dailysummary_df = org_df_list[flie_list.index('Checkmarks.csv')].copy()
dailysummary_column_to_be_merged = dailysummary_df.columns

# food_df
food_df = food_df.rename(columns={'Day': 'Date'})
food_column_to_be_merged = food_df.columns

# new_sleeps
new_sleeps = new_sleeps.rename(columns={'Wake onset': 'Date'})
new_sleeps_column_to_be_merged = ['Date', 'Sleep performance %', 'Respiratory rate (rpm)',
       'Asleep duration (min)', 'In bed duration (min)',
       'Light sleep duration (min)', 'Deep (SWS) duration (min)',
       'REM duration (min)', 'Awake duration (min)', 'Sleep need (min)',
       'Sleep debt (min)', 'Sleep efficiency %', 'Sleep consistency %', 'Nap',
       'Nap Asleep duration (min)', 'Nap In bed duration (min)',
       'Nap Light sleep duration (min)', 'Nap Deep (SWS) duration (min)',
       'Nap REM duration (min)', 'Nap Awake duration (min)']

#new_physic
new_physic = new_physic.rename(columns={'Wake onset': 'Date'})
new_physic_column_to_be_merged = ['Date', 'Recovery score %', 'Resting heart rate (bpm)',
       'Heart rate variability (ms)', 'Skin temp (celsius)', 'Blood oxygen %',
       'Day Strain', 'Energy burned (cal)', 'Max HR (bpm)', 'Average HR (bpm)']




dfs = [checkmark_df[checkmarks_column_to_be_merged],
       dailysummary_df[dailysummary_column_to_be_merged],
       food_df[food_column_to_be_merged],
       new_sleeps[new_sleeps_column_to_be_merged],
       new_physic[new_physic_column_to_be_merged]]

for tmp_df in dfs:
    tmp_df['Date'] = pd.to_datetime(tmp_df['Date'], format='%Y-%m-%d')

# Merge DataFrames on 'Date'
merged_df = dfs[0]
for tmp_df in dfs[1:]:
    merged_df = pd.merge(merged_df, tmp_df, on='Date', how='outer')

merged_df.to_csv('merged.csv')
