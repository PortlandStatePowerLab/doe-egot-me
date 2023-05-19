import pandas as pd
from datetime import datetime

df = pd.read_csv("./ders.csv")

# df['time'] = pd.to_datetime(df.iloc[:,0], unit='s')

# df = df.drop('Time', axis=1)

# df = df.drop('DER0_loc', axis=1)

# first_col = df.pop('time')

# df.insert(0, 'time', first_col)

for i in range(500,5000, len(df.iloc[:,1])*50):
    print(i)
    # df.iloc[]
    # df['DER0_mag'] = i

# df.to_csv('ders.csv', index=False, header=False)