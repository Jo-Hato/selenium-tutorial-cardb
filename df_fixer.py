from tabulate import tabulate
import pandas as pd

with open('out.csv', 'r') as f:
    df = pd.read_csv(f, index_col=0)
    # r2c0: 会社名 型
    # wait a min... shouldn't I filter the html table before parsing it into df?
df = df.iloc[::10,:] # jump-slice (start, end, jump)


print(tabulate(df, headers='keys', tablefmt='psql'))
