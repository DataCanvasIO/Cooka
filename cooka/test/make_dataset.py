# -*- encoding: utf-8 -*-
import pandas as pd
from datetime import datetime
df = pd.read_csv('cooka/test/dataset/diabetes_10k.csv')

df['datetime'] = pd.Series([datetime.now() for i in range(df.shape[0])])
# print(df.dtypes['datetime'])

df.to_csv('cooka/test/dataset/diabetes_10k_datetime.csv', index=False, date_format="%Y-%m-%d %H:%M:%S")
# , date_format='%Y-%m-%d %H:%M:%S'


def parse_date(t):
    format = "%Y-%m-%d %H:%M:%S"
    try:
        return pd.datetime.strptime(t, format)
    except Exception as e:
        return t


df1 = pd.read_csv('cooka/test/dataset/diabetes_10k_datetime.csv', parse_dates=['datetime', 'gender'], date_parser=parse_date)

print(df1.dtypes['datetime'])
# print(df1['datetime'])
print(df1['gender'])
