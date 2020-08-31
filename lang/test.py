import pandas as pd

df = pd.io.parsers.read_csv("lang/totals.csv")
sliceData = df.loc[:, 'transcript']    # Country 열만 자름
sliceData.to_csv('lang/totals_trans.csv', index=False)    # csv로 저장
