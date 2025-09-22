import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import argparse

def analyze_internet_speed(file_path="speedtest-log.csv", output_mode='save'):
    """
    Analyzes internet speed data, finds the slowest time intervals,
    and visualizes overall and hourly performance.

    Args:
        file_path (str): The path to the CSV file.
        output_mode (str): 'save' to save plots, 'show' to display them.
    """
    try:
        # --- 1. Load and Prepare Data ---
        print(f"🔄 Attempting to load data from '{file_path}'...")
        df = pd.read_csv(file_path, thousands=',')
        print("✅ Successfully loaded the CSV file.")

        print("🔄 Cleaning and preparing data...")
        df.rename(columns={
            'timestamp (in UTC)': 'Timestamp',
            'ping (ms)': 'Ping Latency',
            'download (bps)': 'Download Speed (bps)',
            'upload (bps)': 'Upload Speed (bps)'
        }, inplace=True)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        if 'comment' in df.columns:
            df = df.drop(columns=['comment'])
        df['Download Speed (Mbps)'] = df['Download Speed (bps)'] / 1_000_000
        df['Upload Speed (Mbps)'] = df['Upload Speed (bps)'] / 1_000_000
        df.set_index('Timestamp', inplace=True)
        df.sort_index(inplace=True)
        print("✅ Data preparation complete.")

        # --- 2. Find Slowest Intervals (NEW ANALYSIS) ---
        print("\n🔄 Finding the slowest 15-minute intervals...")
        # Resample data into 15-minute bins and calculate the mean for each bin
        resampled_df = df.resample('15T').mean()
        # Drop intervals where no tests were run (NaN values)
        resampled_df.dropna(inplace=True)
        # Sort by the slowest download speed to find the worst periods
        slowest_intervals = resampled_df.sort_values(by='Download Speed (Mbps)', ascending=True)
        print("\n--- 🎯 Top 10 Slowest 15-Minute Intervals ---")
        print(slowest_intervals.head(10))
        print("-------------------------------------------\n")


        # --- 3. Overall Statistical Analysis ---
        stats_df = df[['Ping Latency', 'Download Speed (Mbps)', 'Upload Speed (Mbps)']]
        print("\n--- Overall Performance Statistics ---")
        print(stats_df.describe())
        print("-------------------------------------\n")

        # --- 4. Time-of-Day Analysis ---
        print("🔄 Analyzing performance by hour of day...")
        df['Hour'] = df.index.hour
        hourly_stats = df.groupby('Hour')[['Download Speed (Mbps)', 'Upload Speed (Mbps)', 'Ping Latency']].mean()
        print("\n--- Average Performance by Hour ---")
        print(hourly_stats)
        print("-------------------------------------\n")

        # --- 5. Visualization ---
        print("🔄 Generating plots...")
        # (The code for all three plots remains the same as the last version)
        plt.style.use('seaborn-v0_8-whitegrid')

        # Plot 1: Time Series
        fig1, ax1 = plt.subplots(figsize=(14, 7))
        # ... (full plotting code)
        fig1.autofmt_xdate()
        ax1.set_title('Internet Latency and Speed Over Time')
        ax1.plot(df.index, df['Ping Latency'], color='r', alpha=0.8, label='Ping Latency (ms)')
        ax1.set_xlabel('Date and Time')
        ax1.set_ylabel('Ping Latency (ms)', color='r')
        ax1.tick_params(axis='y', labelcolor='r')
        ax2 = ax1.twinx()
        ax2.plot(df.index, df['Download Speed (Mbps)'], color='g', label='Download Speed (Mbps)')
        ax2.plot(df.index, df['Upload Speed (Mbps)'], color='b', label='Upload Speed (Mbps)')
        ax2.set_ylabel('Speed (Mbps)', color='g')
        ax2.tick_params(axis='y', labelcolor='g')
        ax2.set_ylim(bottom=0)
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left')

        # Plot 2: Distributions
        fig2, axes = plt.subplots(1, 3, figsize=(18, 5))
        # ... (full plotting code)
        df['Ping Latency'].plot(kind='hist', bins=30, ax=axes[0], title='Ping Latency Distribution', color='red', alpha=0.7)
        axes[0].set_xlabel("Latency (ms)")
        df['Download Speed (Mbps)'].plot(kind='hist', bins=30, ax=axes[1], title='Download Speed Distribution', color='green', alpha=0.7)
        axes[1].set_xlabel("Speed (Mbps)")
        df['Upload Speed (Mbps)'].plot(kind='hist', bins=30, ax=axes[2], title='Upload Speed Distribution', color='blue', alpha=0.7)
        axes[2].set_xlabel("Speed (Mbps)")
        fig2.tight_layout()

        # Plot 3: Hourly Performance Bar Chart
        fig3, ax_speed = plt.subplots(figsize=(14, 7))
        # ... (full plotting code)
        ax_speed.set_title('Average Internet Performance by Hour of Day')
        ax_speed.set_xlabel('Hour of Day (0-23)')
        ax_speed.set_ylabel('Average Speed (Mbps)', color='tab:blue')
        hourly_stats['Download Speed (Mbps)'].plot(kind='bar', ax=ax_speed, position=0, width=0.4, color='tab:green', label='Download Speed')
        hourly_stats['Upload Speed (Mbps)'].plot(kind='bar', ax=ax_speed, position=1, width=0.4, color='tab:blue', label='Upload Speed')
        ax_speed.tick_params(axis='y', labelcolor='tab:blue')
        ax_speed.grid(axis='y')
        ax_ping = ax_speed.twinx()
        ax_ping.set_ylabel('Average Ping Latency (ms)', color='tab:red')
        ax_ping.plot(hourly_stats.index, hourly_stats['Ping Latency'], color='tab:red', marker='o', linestyle='--', label='Ping Latency')
        ax_ping.tick_params(axis='y', labelcolor='tab:red')
        ax_speed.set_xticks(range(24))
        ax_speed.set_xticklabels(range(24))
        lines, labels = ax_speed.get_legend_handles_labels()
        lines2, labels2 = ax_ping.get_legend_handles_labels()
        ax_ping.legend(lines + lines2, labels + labels2, loc='upper left')
        fig3.tight_layout()

        # --- 6. Output ---
        if output_mode == 'show':
            print("🖥️ Displaying interactive plots. Close the plot windows to exit.")
            plt.show()
        else:
            fig1.savefig('internet_performance_over_time.png')
            print("✅ Saved plot: 'internet_performance_over_time.png'")
            fig2.savefig('internet_speed_distributions.png')
            print("✅ Saved plot: 'internet_speed_distributions.png'")
            fig3.savefig('hourly_performance.png')
            print("✅ Saved plot: 'hourly_performance.png'")

    except FileNotFoundError:
        print(f"❌ Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Analyze Internet Speed Test Logs.")
    parser.add_argument('--output', type=str, choices=['save', 'show'], default='save', help="'save' plots as files or 'show' them interactively.")
    parser.add_argument('--file', type=str, default='speedtest-log.csv', help="Path to the speedtest CSV log file.")
    args = parser.parse_args()
    analyze_internet_speed(file_path=args.file, output_mode=args.output)
