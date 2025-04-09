import pandas as pd
import matplotlib.pyplot as plt

# Read CSV files
df_upbit = pd.read_csv('upbit-trading-volume-1-year.csv')
df_bithumb = pd.read_csv('bithumb-trading-volume-1-year.csv')

# Convert date format
df_upbit['snapped_at'] = pd.to_datetime(df_upbit['snapped_at'])
df_bithumb['snapped_at'] = pd.to_datetime(df_bithumb['snapped_at'])

# Define the latest date and calculate quarter start dates
latest_date = df_upbit['snapped_at'].max()
one_year_ago = latest_date - pd.DateOffset(years=1)

q1_start = one_year_ago
q2_start = q1_start + pd.DateOffset(months=3)
q3_start = q2_start + pd.DateOffset(months=3)
q4_start = q3_start + pd.DateOffset(months=3)

# Filter data by quarter
df_upbit_q1 = df_upbit[(df_upbit['snapped_at'] >= q1_start) & (df_upbit['snapped_at'] < q2_start)]
df_upbit_q2 = df_upbit[(df_upbit['snapped_at'] >= q2_start) & (df_upbit['snapped_at'] < q3_start)]
df_upbit_q3 = df_upbit[(df_upbit['snapped_at'] >= q3_start) & (df_upbit['snapped_at'] < q4_start)]
df_upbit_q4 = df_upbit[(df_upbit['snapped_at'] >= q4_start)]

df_bithumb_q1 = df_bithumb[(df_bithumb['snapped_at'] >= q1_start) & (df_bithumb['snapped_at'] < q2_start)]
df_bithumb_q2 = df_bithumb[(df_bithumb['snapped_at'] >= q2_start) & (df_bithumb['snapped_at'] < q3_start)]
df_bithumb_q3 = df_bithumb[(df_bithumb['snapped_at'] >= q3_start) & (df_bithumb['snapped_at'] < q4_start)]
df_bithumb_q4 = df_bithumb[(df_bithumb['snapped_at'] >= q4_start)]

# Calculate average trading volume per quarter
upbit_avg_q1 = df_upbit_q1['volume'].mean()
bithumb_avg_q1 = df_bithumb_q1['volume'].mean()
upbit_avg_q2 = df_upbit_q2['volume'].mean()
bithumb_avg_q2 = df_bithumb_q2['volume'].mean()
upbit_avg_q3 = df_upbit_q3['volume'].mean()
bithumb_avg_q3 = df_bithumb_q3['volume'].mean()
upbit_avg_q4 = df_upbit_q4['volume'].mean()
bithumb_avg_q4 = df_bithumb_q4['volume'].mean()

# Prepare data for pie charts
labels = ['Upbit', 'Bithumb']
sizes_q1 = [upbit_avg_q1, bithumb_avg_q1]
sizes_q2 = [upbit_avg_q2, bithumb_avg_q2]
sizes_q3 = [upbit_avg_q3, bithumb_avg_q3]
sizes_q4 = [upbit_avg_q4, bithumb_avg_q4]

# Custom colors for better visualization
colors = ['#ff6f61', '#3498db']  # Upbit (Red-Orange), Bithumb (Blue)

# Define explode values (highlight larger market share)
explode_q1 = [0.05 if upbit_avg_q1 > bithumb_avg_q1 else 0, 0.05 if bithumb_avg_q1 > upbit_avg_q1 else 0]
explode_q2 = [0.05 if upbit_avg_q2 > bithumb_avg_q2 else 0, 0.05 if bithumb_avg_q2 > upbit_avg_q2 else 0]
explode_q3 = [0.05 if upbit_avg_q3 > bithumb_avg_q3 else 0, 0.05 if bithumb_avg_q3 > upbit_avg_q3 else 0]
explode_q4 = [0.05 if upbit_avg_q4 > bithumb_avg_q4 else 0, 0.05 if bithumb_avg_q4 > upbit_avg_q4 else 0]

# Create pie charts with improved styling
fig, axes = plt.subplots(2, 2, figsize=(14, 14))

# Q1 Pie Chart
axes[0, 0].pie(sizes_q1, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140, explode=explode_q1, shadow=True, wedgeprops={'edgecolor': 'black'})
axes[0, 0].set_title('Q1 Trading Volume Share', fontsize=14, fontweight='bold')

# Q2 Pie Chart
axes[0, 1].pie(sizes_q2, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140, explode=explode_q2, shadow=True, wedgeprops={'edgecolor': 'black'})
axes[0, 1].set_title('Q2 Trading Volume Share', fontsize=14, fontweight='bold')

# Q3 Pie Chart
axes[1, 0].pie(sizes_q3, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140, explode=explode_q3, shadow=True, wedgeprops={'edgecolor': 'black'})
axes[1, 0].set_title('Q3 Trading Volume Share', fontsize=14, fontweight='bold')

# Q4 Pie Chart
axes[1, 1].pie(sizes_q4, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140, explode=explode_q4, shadow=True, wedgeprops={'edgecolor': 'black'})
axes[1, 1].set_title('Q4 Trading Volume Share', fontsize=14, fontweight='bold')

# Add a main title
plt.suptitle('Upbit vs Bithumb Quarterly Trading Volume Comparison', fontsize=16, fontweight='bold')

# Adjust layout for better spacing
plt.tight_layout(rect=[0, 0.03, 1, 0.97])

# Show the charts
plt.show()
