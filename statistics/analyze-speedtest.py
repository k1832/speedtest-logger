import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_prepare_data(file_path: str) -> pd.DataFrame | None:
    """Loads, cleans, and prepares the speedtest data from a CSV file."""
    print("🔄 Loading and preparing your data...")
    try:
        df = pd.read_csv(file_path, thousands=',')
    except FileNotFoundError:
        print(f"❌ ERROR: File not found at '{file_path}'.")
        return None
    except Exception as e:
        print(f"❌ An error occurred while reading the file: {e}")
        return None

    df.rename(columns={
        'timestamp (UTC)': 'timestamp_utc',
        'ping (ms)': 'ping',
        'download (Mbps)': 'download_mbps',
        'upload (Mbps)': 'upload_mbps'
    }, inplace=True)

    # Define the columns that should be numeric
    numeric_cols = ['ping', 'download_mbps', 'upload_mbps']

    # Check for required columns AFTER renaming
    required_cols = ['timestamp_utc'] + numeric_cols
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        print(f"❌ ERROR: DataFrame is missing required columns after renaming: {missing}. Check original CSV headers.")
        return None

    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df.dropna(subset=numeric_cols, inplace=True)

    if df.empty:
        print("❌ ERROR: No valid data remains after cleaning.")
        return None

    df.set_index(pd.to_datetime(df['timestamp_utc']).dt.tz_convert('Asia/Tokyo'), inplace=True)
    df.index.name = 'timestamp_jst'

    df['hour'] = df.index.hour
    df['day_of_week'] = df.index.day_name()
    df['day_type'] = df.index.to_series().apply(lambda x: 'Weekday' if x.dayofweek < 5 else 'Weekend')

    print("✅ Data successfully loaded.")
    return df

def plot_performance_over_time(df: pd.DataFrame):
    """Generates time-series plots for download, upload, and ping."""
    print("📈 Generating Time Series Plots...")
    fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=True)
    fig.suptitle('Internet Performance Over Time (JST)', fontsize=16)

    sns.lineplot(data=df, x=df.index, y='download_mbps', ax=axes[0], color='blue')
    axes[0].set(title='Download Speed Over Time', ylabel='Download Speed (Mbps)')
    axes[0].grid(True)

    sns.lineplot(data=df, x=df.index, y='upload_mbps', ax=axes[1], color='green')
    axes[1].set(title='Upload Speed Over Time', ylabel='Upload Speed (Mbps)')
    axes[1].grid(True)

    sns.lineplot(data=df, x=df.index, y='ping', ax=axes[2], color='red')
    axes[2].set(title='Ping Latency Over Time', ylabel='Ping (ms)', xlabel='Date and Time (JST)')
    axes[2].grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

def plot_performance_by_hour(df: pd.DataFrame):
    """Generates bar plots of average performance for each hour of the day."""
    print("🕔 Generating Time-of-Day Analysis Plots...")
    hourly_stats = df.groupby('hour')[['download_mbps', 'upload_mbps', 'ping']].mean()

    fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=True)
    fig.suptitle('Average Performance by Hour of Day (JST)', fontsize=16)

    sns.barplot(data=hourly_stats, x=hourly_stats.index, y='download_mbps', ax=axes[0], hue=hourly_stats.index, palette='viridis', legend=False)
    axes[0].set(title='Average Download Speed by Hour', ylabel='Avg. Download Speed (Mbps)')

    sns.barplot(data=hourly_stats, x=hourly_stats.index, y='upload_mbps', ax=axes[1], hue=hourly_stats.index, palette='viridis', legend=False)
    axes[1].set(title='Average Upload Speed by Hour', ylabel='Avg. Upload Speed (Mbps)')

    sns.barplot(data=hourly_stats, x=hourly_stats.index, y='ping', ax=axes[2], hue=hourly_stats.index, palette='viridis', legend=False)
    axes[2].set(title='Average Ping Latency by Hour', ylabel='Avg. Ping (ms)', xlabel='Hour of Day (0-23)')

    plt.tight_layout(rect=[0, 0, 1, 0.96])

def plot_performance_by_day_of_week(df: pd.DataFrame):
    """Generates bar plots of average performance for each day of the week."""
    print("🗓️ Generating Day-of-Week Analysis Plots...")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_stats = df.groupby('day_of_week')[['download_mbps', 'upload_mbps', 'ping']].mean().reindex(day_order)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Average Performance by Day of Week (JST)', fontsize=16)

    for i, metric in enumerate(['download_mbps', 'upload_mbps', 'ping']):
        sns.barplot(data=daily_stats, x=daily_stats.index, y=metric, ax=axes[i], hue=daily_stats.index, palette='plasma', legend=False)
        axes[i].set_title(f"Average {metric.replace('_mbps', ' Speed (Mbps)').replace('ping', 'Ping (ms)')} by Day")
        axes[i].set_ylabel(f"Avg. {metric.split('_')[0].capitalize()} ({'Mbps' if 'mbps' in metric else 'ms'})")
        axes[i].tick_params(axis='x', rotation=45)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

def plot_distributions_and_correlation(df: pd.DataFrame):
    """Generates distribution histograms and a correlation matrix heatmap."""
    print("🧑‍🤝‍🧑 Generating Correlation and Distribution Plots...")

    plt.figure(figsize=(8, 6))
    sns.heatmap(df[['ping', 'download_mbps', 'upload_mbps']].corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix of Performance Metrics')

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Distribution of Performance Metrics', fontsize=16)
    sns.histplot(data=df, x='download_mbps', kde=True, ax=axes[0], color='skyblue').set_title('Download Speed Distribution')
    sns.histplot(data=df, x='upload_mbps', kde=True, ax=axes[1], color='olive').set_title('Upload Speed Distribution')
    sns.histplot(data=df, x='ping', kde=True, ax=axes[2], color='gold').set_title('Ping Latency Distribution')

    plt.tight_layout(rect=[0, 0, 1, 0.95])

def plot_weekday_vs_weekend_performance(df: pd.DataFrame):
    """Generates line and heatmaps comparing weekday and weekend performance."""
    print("👨‍💻 Generating Weekday vs. Weekend Hourly Plots...")
    cross_stats = df.groupby(['day_type', 'hour'])[['download_mbps', 'ping']].mean().reset_index()

    fig, axes = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    fig.suptitle('Weekday vs. Weekend Performance by Hour', fontsize=16)

    sns.lineplot(data=cross_stats, x='hour', y='download_mbps', hue='day_type', ax=axes[0], marker='o')
    axes[0].set(title='Average Download Speed', ylabel='Download Speed (Mbps)')
    axes[0].grid(True)

    sns.lineplot(data=cross_stats, x='hour', y='ping', hue='day_type', ax=axes[1], marker='o')
    axes[1].set(title='Average Ping Latency', ylabel='Ping (ms)', xlabel='Hour of Day (JST)')
    axes[1].grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    plt.figure(figsize=(12, 6))
    heatmap_data = cross_stats.pivot(index='day_type', columns='hour', values='download_mbps')
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="rocket_r", linewidths=.5)
    plt.title('Heatmap of Average Download Speed (Mbps) by Hour and Day Type')
    plt.xlabel('Hour of Day (JST)')
    plt.ylabel('')
    plt.tight_layout()

def analyze_internet_speed(file_path: str):
    """Main function to run the complete analysis workflow."""
    df = load_and_prepare_data(file_path)
    if df is None:
        return

    print("-" * 50)
    print("📊 DESCRIPTIVE STATISTICS")
    print(df[['ping', 'download_mbps', 'upload_mbps']].describe())
    print("-" * 50)

    plot_performance_over_time(df)
    plot_performance_by_hour(df)
    plot_performance_by_day_of_week(df)
    plot_distributions_and_correlation(df)
    plot_weekday_vs_weekend_performance(df)

    print("\n✅ Analysis complete. Displaying all plots now...")
    plt.show()

def main():
    """Defines the file path and initiates the analysis."""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        base_path = os.getcwd()

    data_dir_path = os.path.join(base_path, "data")
    file_path = os.path.join(data_dir_path, "speedtest-log.csv")
    analyze_internet_speed(file_path)

if __name__ == "__main__":
    main()
