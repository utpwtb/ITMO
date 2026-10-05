import pandas as pd
import matplotlib.pyplot as plt

# 读取CSV文件
df = pd.read_csv('data.csv')

# 重命名列名（移除尖括号）
df.columns = [col.strip('<>') for col in df.columns]

# 将DATE列转换为日期格式
df['DATE'] = pd.to_datetime(df['DATE'])

# 选择指定日期的数据
dates = ['2018-09-07', '2018-10-09', '2018-11-07', '2018-12-07']
dates = [pd.to_datetime(date) for date in dates]

# 创建图形和子图
fig, ax = plt.subplots(figsize=(20, 10))

# 定义颜色和标签
labels = ['OPEN', 'HIGH', 'LOW', 'CLOSE']
colors = ['blue', 'green', 'red', 'purple']
boxes = []

# 为每个日期绘制四个箱线图
positions = range(1, 17)  # 1到16的位置
current_pos = 0

for date in dates:
    day_data = df[df['DATE'].dt.date == date.date()]
    if not day_data.empty:
        for label, color in zip(labels, colors):
            bp = ax.boxplot(day_data[label], 
                          positions=[positions[current_pos]],
                          patch_artist=True,
                          tick_labels=[f'{date.strftime("%m-%d")}\n{label}'])
            
            # 设置颜色
            for patch in bp['boxes']:
                patch.set_facecolor(color)
                boxes.append(patch)
            current_pos += 1

# 设置图表属性
plt.ylabel('Price')
plt.grid(True)
plt.xticks(positions, rotation=45)

# 添加图例
plt.legend(boxes[:4], labels, loc='upper right')

# 调整布局
plt.tight_layout()
plt.show()
