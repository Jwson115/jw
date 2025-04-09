import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Read CSV files
df_upbit = pd.read_csv('upbit-trading-volume-1-year (1).csv')
df_bithumb = pd.read_csv('bithumb-trading-volume-1-year (1).csv')

# Convert date format
df_upbit['snapped_at'] = pd.to_datetime(df_upbit['snapped_at'])
df_bithumb['snapped_at'] = pd.to_datetime(df_bithumb['snapped_at'])

# Define the latest date and adjust to the start of the month
latest_date = df_upbit['snapped_at'].max()
latest_month_start = latest_date.replace(day=1)  # Set to the first day of the latest month
four_months_ago = latest_month_start - pd.DateOffset(months=3)  # Get start of the fourth most recent month

# Generate a list of month start dates
month_starts = [four_months_ago + pd.DateOffset(months=i) for i in range(4)]
month_labels = [date.strftime('%b %Y') for date in month_starts]  # Format as "Jan 2024", etc.

# Store pie chart data
upbit_avg_months = []
bithumb_avg_months = []

# Calculate average trading volume per month
for i in range(4):
    start_date = month_starts[i]
    end_date = start_date + pd.DateOffset(months=1)

    df_upbit_month = df_upbit[(df_upbit['snapped_at'] >= start_date) & (df_upbit['snapped_at'] < end_date)]
    df_bithumb_month = df_bithumb[(df_bithumb['snapped_at'] >= start_date) & (df_bithumb['snapped_at'] < end_date)]

    upbit_avg = df_upbit_month['volume'].mean()
    bithumb_avg = df_bithumb_month['volume'].mean()

    upbit_avg_months.append(upbit_avg)
    bithumb_avg_months.append(bithumb_avg)

# Custom colors
colors = ['#ff6f61', '#3498db']  # Upbit (Red-Orange), Bithumb (Blue)

# Create pie charts
fig = plt.figure(figsize=(16, 6))
gs = gridspec.GridSpec(1, 4, figure=fig)  # 1 row, 4 columns

for i in range(4):
    ax = fig.add_subplot(gs[0, i])  # Arrange in 1x4 grid
    sizes = [upbit_avg_months[i], bithumb_avg_months[i]]
    explode = [0.05 if upbit_avg_months[i] > bithumb_avg_months[i] else 0, 0.05 if bithumb_avg_months[i] > upbit_avg_months[i] else 0]

    ax.pie(sizes, labels=['Upbit', 'Bithumb'], autopct='%1.1f%%', colors=colors, startangle=140, explode=explode, shadow=True, wedgeprops={'edgecolor': 'black'})
    ax.set_title(month_labels[i], fontsize=12, fontweight='bold')

# Add main title
plt.suptitle('Upbit vs Bithumb Monthly Trading Volume Comparison (Last 4 Months)', fontsize=16, fontweight='bold')

# Adjust layout
plt.tight_layout(rect=[0, 0.03, 1, 0.97])

# Show charts
plt.show()