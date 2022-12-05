from tabulate import tabulate
import pandas as pd

with open('out.csv', 'r') as f:
    df = pd.read_csv(f, index_col=0)
df = df.iloc[::10,:] # jump-slice (start, end, jump)

print(tabulate(df, headers='keys', tablefmt='psql'))
