import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec

# Read CSV files
df_upbit = pd.read_csv('upbit-trading-volume-1-year.csv')
df_bithumb = pd.read_csv('bithumb-trading-volume-1-year.csv')

# Convert date format
df_upbit['snapped_at'] = pd.to_datetime(df_upbit['snapped_at'])
df_bithumb['snapped_at'] = pd.to_datetime(df_bithumb['snapped_at'])

# Define the latest date and calculate monthly start dates
latest_date = df_upbit['snapped_at'].max()
one_year_ago = latest_date - pd.DateOffset(years=1)

# Generate a list of month start dates
month_starts = [one_year_ago + pd.DateOffset(months=i) for i in range(12)]
month_labels = [date.strftime('%b %Y') for date in month_starts]  # Format as "Jan 2024", etc.

# Store average monthly trading volume
upbit_avg_months = []
bithumb_avg_months = []

# Calculate average trading volume per month
for i in range(12):
    start_date = month_starts[i]
    end_date = start_date + pd.DateOffset(months=1)

    df_upbit_month = df_upbit[(df_upbit['snapped_at'] >= start_date) & (df_upbit['snapped_at'] < end_date)]
    df_bithumb_month = df_bithumb[(df_bithumb['snapped_at'] >= start_date) & (df_bithumb['snapped_at'] < end_date)]

    upbit_avg = df_upbit_month['volume'].mean()
    bithumb_avg = df_bithumb_month['volume'].mean()

    upbit_avg_months.append(upbit_avg)
    bithumb_avg_months.append(bithumb_avg)

# Custom colors
colors = ['#e74c3c', '#3498db']  # Upbit (Red), Bithumb (Blue)

# Create a figure with GridSpec (1 row for line chart, 3 rows for pie charts)
fig = plt.figure(figsize=(18, 18))
gs = gridspec.GridSpec(5, 4, figure=fig, height_ratios=[1.8, 1, 1, 1, 0.3])  # More balanced spacing

# --- Line Chart (First Row) ---
ax1 = fig.add_subplot(gs[0, :])  # Spanning all columns

# Upbit Trading Volume (Red, Circle Markers)
ax1.plot(df_upbit['snapped_at'], df_upbit['volume'], marker='o', markersize=3, linestyle='-', linewidth=1.5, alpha=0.8, color=colors[0], label='Upbit')

# Bithumb Trading Volume (Blue, Square Markers)
ax1.plot(df_bithumb['snapped_at'], df_bithumb['volume'], marker='s', markersize=3, linestyle='-', linewidth=1.5, alpha=0.8, color=colors[1], label='Bithumb')

# Chart Title & Labels
ax1.set_title('Upbit vs Bithumb 1-Year Trading Volume', fontsize=18, fontweight='bold', pad=15)
ax1.set_xlabel('Date', fontsize=13)
ax1.set_ylabel('Trading Volume (Billion $)', fontsize=13)

# Y-axis Formatter (Convert to Billions)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x / 1e9:.1f}B'))

# X-axis Formatting
ax1.tick_params(axis='x', rotation=20)

# Add Grid
ax1.grid(True, linestyle='--', alpha=0.6)

# Customize Legend
ax1.legend(fontsize=12, loc='upper left', frameon=True, edgecolor='gray')

# --- Pie Charts (3x4 Grid) ---
for i in range(12):
    ax = fig.add_subplot(gs[(i // 4) + 1, i % 4])  # 3 rows, 4 columns
    sizes = [upbit_avg_months[i], bithumb_avg_months[i]]
    explode = [0.05 if upbit_avg_months[i] > bithumb_avg_months[i] else 0, 0.05 if bithumb_avg_months[i] > upbit_avg_months[i] else 0]

    ax.pie(sizes, labels=['Upbit', 'Bithumb'], autopct='%1.1f%%', colors=colors, startangle=140, explode=explode, shadow=True, wedgeprops={'edgecolor': 'black'})
    ax.set_title(month_labels[i], fontsize=13, fontweight='bold')

# --- Explanation Text Below Pie Charts ---
ax_desc = fig.add_subplot(gs[4, :])  # Last row for description
ax_desc.axis("off")  # Hide axis

explanation = (
    "pie charts represent the average monthly trading volume"
)

ax_desc.text(0.5, 0.5, explanation, ha="center", va="center", fontsize=13, wrap=True, 
             bbox=dict(facecolor='white', alpha=0.75, edgecolor='black', boxstyle='round,pad=0.5'))

# Adjust layout
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Show combined figure
plt.show()
  