import pandas as pd

df = pd.read_csv('summary.csv', index_col=0, header=0)

filenames = df['filename']
sources = []
for f in filenames:
    parts = f.split('-')
    source = parts[-1][:-4]
    sources.append(source)

df['source num'] = sources

df.to_csv('summary_new.csv')