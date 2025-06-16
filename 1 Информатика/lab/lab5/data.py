import pandas as pd

# 读取CSV文件
df = pd.read_csv('SPFB.RTS-12.18_180901_181231.csv')

# 选择需要的列并创建新的DataFrame
df_new = df[['<DATE>','<TIME>','<OPEN>','<HIGH>','<LOW>','<CLOSE>']].copy()

# 转换DATE列为datetime格式，指定正确的格式
df_new['<DATE>'] = pd.to_datetime(df_new['<DATE>'], format='%d/%m/%y')

# 筛选特定日期的数据
specific_dates = ['2018-09-07', '2018-10-09', '2018-11-07', '2018-12-07']
specific_dates = [pd.to_datetime(date) for date in specific_dates]
df_filtered = df_new[df_new['<DATE>'].isin(specific_dates)]

# 保存筛选后的数据到新的CSV文件
df_filtered.to_csv('data.csv', index=False)
