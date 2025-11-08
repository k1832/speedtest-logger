import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import gspread
from google.oauth2.service_account import Credentials
import os

# Set global plot parameters for a consistent look
plt.rcParams.update({
    'figure.titlesize': 18,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
})

@st.cache_data(ttl=600)
def load_data(use_local_csv: bool) -> pd.DataFrame | None:
    """Loads data from a local CSV file or Google Sheets based on the toggle."""
    data_source_log_prefix = "Sourcing data from"
    if use_local_csv:
        st.info(f"{data_source_log_prefix} local CSV file...")
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, "data", "speedtest-log.csv")
        try:
            df = pd.read_csv(file_path)
            st.success("✅ Successfully loaded data from local CSV.")
            return df
        except FileNotFoundError:
            st.error(f"❌ ERROR: Local file not found at '{file_path}'. Please check the path. \nNote: This option does not work on the streamlit website.")
            return None
        except Exception as e:
            st.error(f"❌ An error occurred while reading the local CSV file: {e}")
            return None
    else:
        st.info(f"{data_source_log_prefix} Google Sheet...")
        try:
            creds_dict = st.secrets["gcp_service_account"]
            scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            gc = gspread.authorize(creds)
            spreadsheet = gc.open("speedtest-log")
            worksheet = spreadsheet.worksheet("2025")
            data = worksheet.get_all_records(numericise_ignore=['all'])
            df = pd.DataFrame(data)
            st.success("✅ Successfully connected and loaded data from Google Sheet.")
            return df
        except Exception as e:
            st.error(f"❌ Failed to connect or load data from Google Sheets: {e}")
            return None

def prepare_data(df: pd.DataFrame) -> pd.DataFrame | None:
    """Cleans, processes, and prepares the speedtest data DataFrame."""
    if df is None or df.empty:
        st.warning("Input DataFrame is empty. Cannot prepare data.")
        return None

    df.rename(columns={
        'timestamp (UTC)': 'timestamp_utc',
        'ping (ms)': 'ping',
        'download (Mbps)': 'download_mbps',
        'upload (Mbps)': 'upload_mbps'
    }, inplace=True)

    numeric_cols = ['ping', 'download_mbps', 'upload_mbps']
    required_cols = ['timestamp_utc'] + numeric_cols
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        st.error(f"❌ ERROR: DataFrame is missing required columns: {missing}. Check your data source headers.")
        return None

    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df.dropna(subset=numeric_cols, inplace=True)

    if df.empty:
        st.error("❌ ERROR: No valid numeric data remains after cleaning.")
        return None

    # Create a datetime Series, extract features, and then set as index
    datetime_jst = pd.to_datetime(df['timestamp_utc']).dt.tz_convert('Asia/Tokyo')
    df['hour'] = datetime_jst.dt.hour
    df['day_of_week'] = datetime_jst.dt.day_name()
    df['day_type'] = datetime_jst.dt.dayofweek.apply(lambda x: 'Weekday' if x < 5 else 'Weekend')
    df.set_index(datetime_jst, inplace=True)
    df.index.name = 'timestamp_jst'

    return df

# --- NEW COMPARISON FUNCTIONS ---

def display_comparison_metrics(before_df: pd.DataFrame, after_df: pd.DataFrame):
    """Calculates and displays overall metrics for 'Before' vs 'After'."""
    st.header("📊 Overall Performance Shift")

    if before_df.empty or after_df.empty:
        st.warning("Cannot display comparison metrics. One or both periods have no data.")
        return

    before_avg = before_df[['download_mbps', 'upload_mbps', 'ping']].mean()
    after_avg = after_df[['download_mbps', 'upload_mbps', 'ping']].mean()

    def calculate_delta(current, historical):
        if historical == 0: return 0
        return ((current - historical) / historical) * 100

    delta_dl = calculate_delta(after_avg['download_mbps'], before_avg['download_mbps'])
    delta_ul = calculate_delta(after_avg['upload_mbps'], before_avg['upload_mbps'])
    delta_ping = calculate_delta(after_avg['ping'], before_avg['ping'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Download (After vs Before)",
            value=f"{after_avg['download_mbps']:.1f} Mbps",
            delta=f"{delta_dl:.1f}%",
            delta_color="normal"
        )
    with col2:
        st.metric(
            label="Upload (After vs Before)",
            value=f"{after_avg['upload_mbps']:.1f} Mbps",
            delta=f"{delta_ul:.1f}%",
            delta_color="normal"
        )
    with col3:
        st.metric(
            label="Ping (After vs Before)",
            value=f"{after_avg['ping']:.1f} ms",
            delta=f"{delta_ping:.1f}%",
            delta_color="inverse"  # Lower ping is better
        )

def plot_comparison_over_time(all_data_df: pd.DataFrame, change_time: pd.Timestamp):
    """Plots performance over time, highlighting the plan change."""
    st.header("📈 Performance Over Time (All Data)")

    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True, constrained_layout=True)
    fig.suptitle('Internet Performance Over Time (JST)')

    # Download
    sns.lineplot(data=all_data_df, x=all_data_df.index, y='download_mbps', ax=axes[0], color='blue')
    axes[0].set(title='Download Speed Over Time', ylabel='Download Speed\n(Mbps)')
    axes[0].grid(True)

    # Upload
    sns.lineplot(data=all_data_df, x=all_data_df.index, y='upload_mbps', ax=axes[1], color='green')
    axes[1].set(title='Upload Speed Over Time', ylabel='Upload Speed\n(Mbps)')
    axes[1].grid(True)

    # Ping
    sns.lineplot(data=all_data_df, x=all_data_df.index, y='ping', ax=axes[2], color='red')
    axes[2].set(title='Ping Latency Over Time', ylabel='Ping\n(ms)', xlabel='Date and Time (JST)')
    axes[2].grid(True)

    # Add vertical line for plan change
    for ax in axes:
        ax.axvline(x=change_time, color='purple', linestyle='--', linewidth=2, label='Plan Change')

    # Add legend to the first plot
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    fig.autofmt_xdate()
    st.pyplot(fig)

def plot_comparison_by_hour(before_df: pd.DataFrame, after_df: pd.DataFrame):
    """Plots average performance by hour, comparing Before and After."""
    st.header("🕔 Performance by Hour of Day (Before vs. After)")

    if before_df.empty or after_df.empty:
        st.warning("Cannot display hourly comparison. One or both periods have no data.")
        return

    before_hourly = before_df.groupby('hour')[['download_mbps', 'upload_mbps', 'ping']].mean().reset_index()
    before_hourly['Period'] = 'Before'

    after_hourly = after_df.groupby('hour')[['download_mbps', 'upload_mbps', 'ping']].mean().reset_index()
    after_hourly['Period'] = 'After'

    combined_hourly = pd.concat([before_hourly, after_hourly], ignore_index=True)

    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True, constrained_layout=True)
    fig.suptitle('Average Performance by Hour of Day (JST)')

    sns.lineplot(data=combined_hourly, x='hour', y='download_mbps', hue='Period', ax=axes[0], marker='o')
    axes[0].set(title='Average Download Speed by Hour', ylabel='Avg. Download Speed (Mbps)')
    axes[0].grid(True)

    sns.lineplot(data=combined_hourly, x='hour', y='upload_mbps', hue='Period', ax=axes[1], marker='o')
    axes[1].set(title='Average Upload Speed by Hour', ylabel='Avg. Upload Speed (Mbps)')
    axes[1].grid(True)

    sns.lineplot(data=combined_hourly, x='hour', y='ping', hue='Period', ax=axes[2], marker='o')
    axes[2].set(title='Average Ping Latency by Hour', ylabel='Avg. Ping (ms)', xlabel='Hour of Day (0-23)')
    axes[2].grid(True)

    axes[2].set_xticks(range(0, 24))

    st.pyplot(fig)

def plot_comparison_by_day_of_week(before_df: pd.DataFrame, after_df: pd.DataFrame):
    """Plots average performance by day, comparing Before and After."""
    st.header("🗓️ Performance by Day of Week (Before vs. After)")

    if before_df.empty or after_df.empty:
        st.warning("Cannot display daily comparison. One or both periods have no data.")
        return

    # Removed early reindexing. We will let seaborn handle the order.
    before_daily = before_df.groupby('day_of_week')[['download_mbps', 'upload_mbps', 'ping']].mean().reset_index()
    before_daily['Period'] = 'Before'

    after_daily = after_df.groupby('day_of_week')[['download_mbps', 'upload_mbps', 'ping']].mean().reset_index()
    after_daily['Period'] = 'After'

    combined_daily = pd.concat([before_daily, after_daily], ignore_index=True)

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)
    fig.suptitle('Average Performance by Day of Week (JST)')

    metrics = ['download_mbps', 'upload_mbps', 'ping']
    titles = ['Download Speed (Mbps)', 'Upload Speed (Mbps)', 'Ping (ms)']

    for i, (metric, title) in enumerate(zip(metrics, titles)):
        # Added 'order=day_order' to explicitly tell seaborn the order of bars
        sns.barplot(data=combined_daily, x='day_of_week', y=metric, hue='Period', ax=axes[i], order=day_order)
        axes[i].set_title(f"Average {title}")
        axes[i].set_ylabel(f"Average {title}")
        axes[i].set_xlabel("")
        axes[i].tick_params(axis='x', rotation=45)
        if i > 0: axes[i].get_legend().remove()

    st.pyplot(fig)

def plot_comparison_distributions(before_df: pd.DataFrame, after_df: pd.DataFrame):
    """Plots distributions for metrics, comparing Before and After."""
    st.header("📊 Metric Distributions (Before vs. After)")

    if before_df.empty or after_df.empty:
        st.warning("Cannot display distribution comparison. One or both periods have no data.")
        return

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)
    fig.suptitle('Distribution of Performance Metrics')

    # Download
    sns.histplot(data=before_df, x='download_mbps', kde=True, ax=axes[0], color='blue', label='Before', stat='density')
    sns.histplot(data=after_df, x='download_mbps', kde=True, ax=axes[0], color='orange', label='After', stat='density')
    axes[0].set_title('Download Distribution')
    axes[0].legend()

    # Upload
    sns.histplot(data=before_df, x='upload_mbps', kde=True, ax=axes[1], color='blue', label='Before', stat='density')
    sns.histplot(data=after_df, x='upload_mbps', kde=True, ax=axes[1], color='orange', label='After', stat='density')
    axes[1].set_title('Upload Distribution')
    axes[1].legend()

    # Ping
    sns.histplot(data=before_df, x='ping', kde=True, ax=axes[2], color='blue', label='Before', stat='density')
    sns.histplot(data=after_df, x='ping', kde=True, ax=axes[2], color='orange', label='After', stat='density')
    axes[2].set_title('Ping Distribution')
    axes[2].legend()

    st.pyplot(fig)

# --- ORIGINAL PLOTTING FUNCTIONS (for individual tabs) ---

def plot_distributions_and_correlation(df: pd.DataFrame, period_title: str):
    st.header("🧑‍🤝‍🧑 Correlations and Distributions")
    st.subheader(f"For '{period_title}' Period")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Correlation Matrix")
        fig1, ax1 = plt.subplots(figsize=(6, 5), constrained_layout=True)
        sns.heatmap(df[['ping', 'download_mbps', 'upload_mbps']].corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax1)
        st.pyplot(fig1)

    with col2:
        st.subheader("Metric Distributions")
        fig2, axes = plt.subplots(1, 3, figsize=(12, 5), constrained_layout=True)
        sns.histplot(data=df, x='download_mbps', kde=True, ax=axes[0], color='skyblue').set_title('Download')
        sns.histplot(data=df, x='upload_mbps', kde=True, ax=axes[1], color='olive').set_title('Upload')
        sns.histplot(data=df, x='ping', kde=True, ax=axes[2], color='gold').set_title('Ping')
        st.pyplot(fig2)

def plot_weekday_vs_weekend_performance(df: pd.DataFrame, period_title: str):
    st.header("👨‍💻 Weekday vs. Weekend Performance")
    st.subheader(f"For '{period_title}' Period")

    cross_stats = df.groupby(['day_type', 'hour'])[['download_mbps', 'ping']].mean().reset_index()

    fig1, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True, constrained_layout=True)
    fig1.suptitle('Weekday vs. Weekend Performance by Hour')
    sns.lineplot(data=cross_stats, x='hour', y='download_mbps', hue='day_type', ax=axes[0], marker='o')
    axes[0].set(title='Average Download Speed', ylabel='Download Speed (Mbps)')
    axes[0].grid(True)
    sns.lineplot(data=cross_stats, x='hour', y='ping', hue='day_type', ax=axes[1], marker='o')
    axes[1].set(title='Average Ping Latency', ylabel='Ping (ms)', xlabel='Hour of Day (JST)')
    axes[1].grid(True)
    axes[1].set_xticks(range(0, 24))
    st.pyplot(fig1)

    st.subheader("Download Speed Heatmap (Mbps)")
    try:
        heatmap_data = cross_stats.pivot(index='day_type', columns='hour', values='download_mbps')
        fig2, ax2 = plt.subplots(figsize=(12, 2.5), constrained_layout=True)
        sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="rocket_r", linewidths=.5, ax=ax2)
        ax2.set(title='Average Download Speed (Mbps) by Hour and Day Type', xlabel='Hour of Day (JST)', ylabel='')
        st.pyplot(fig2)
    except ValueError:
        st.warning("Not enough varied data (e.g., missing all weekend data) to create a Weekday vs. Weekend heatmap.")


def plot_overall_stats(df: pd.DataFrame, period_title: str):
    st.header("🔢 Overall Statistics")
    st.subheader(f"For '{period_title}' Period")
    st.dataframe(df[['ping', 'download_mbps', 'upload_mbps']].describe())

# --- MAIN FUNCTION ---

def main():
    """Main function to build and run the Streamlit app."""
    st.set_page_config(page_title="Speedtest Comparison", layout="wide")

    # --- Configuration ---
    # HARDCODED plan change time as requested
    PLAN_CHANGE_TIME_STR = "2025-11-06 19:06:00"
    PLAN_CHANGE_TIME_JST = pd.to_datetime(PLAN_CHANGE_TIME_STR).tz_localize('Asia/Tokyo')
    # --- End Configuration ---

    if st.secrets.get("local", False):
        st.sidebar.header("⚙️ Data Source Configuration")
        use_local = st.sidebar.toggle("Use Local CSV", help="If on, loads data from local CSV. If off, fetches from Google Sheets.")
    else:
        use_local = False

    st.title("📊 Internet Plan Performance Dashboard")
    st.markdown(f"Analyzing performance before and after the plan change on **{PLAN_CHANGE_TIME_STR} JST**")

    raw_df = load_data(use_local_csv=use_local)

    if raw_df is not None:
        all_data_df = prepare_data(raw_df)

        if all_data_df is not None:
            # --- Split Data ---
            before_df = all_data_df[all_data_df.index < PLAN_CHANGE_TIME_JST]
            after_df = all_data_df[all_data_df.index >= PLAN_CHANGE_TIME_JST]

            st.success(f"Loaded and processed {len(all_data_df)} total records.")
            st.info(f"Found **{len(before_df)}** records 'Before' and **{len(after_df)}** records 'After' the plan change.")

            if before_df.empty:
                st.error("No data found 'Before' the plan change time. Check the date or your data source.")
            if after_df.empty:
                st.error("No data found 'After' the plan change time. Check the date or your data source.")

            # --- Create Tabs ---
            tab_comp, tab_before, tab_after = st.tabs([
                "📊 Comparison",
                "📉 Before Plan Analysis",
                "📈 After Plan Analysis"
            ])

            with tab_comp:
                st.header("Side-by-Side Comparison")
                if not before_df.empty and not after_df.empty:
                    display_comparison_metrics(before_df, after_df)
                    plot_comparison_over_time(all_data_df, PLAN_CHANGE_TIME_JST)
                    plot_comparison_by_hour(before_df, after_df)
                    plot_comparison_by_day_of_week(before_df, after_df)
                    plot_comparison_distributions(before_df, after_df)
                else:
                    st.warning("Cannot generate comparison plots as one or both time periods have no data.")

            with tab_before:
                st.header("Deep Dive: 'Before' Period")
                if not before_df.empty:
                    plot_overall_stats(before_df, "Before")
                    plot_weekday_vs_weekend_performance(before_df, "Before")
                    plot_distributions_and_correlation(before_df, "Before")
                    with st.expander("Show 'Before' Raw Data"):
                        st.dataframe(before_df)
                else:
                    st.warning("No data to display for the 'Before' period.")

            with tab_after:
                st.header("Deep Dive: 'After' Period")
                if not after_df.empty:
                    plot_overall_stats(after_df, "After")
                    plot_weekday_vs_weekend_performance(after_df, "After")
                    plot_distributions_and_correlation(after_df, "After")
                    with st.expander("Show 'After' Raw Data"):
                        st.dataframe(after_df)
                else:
                    st.warning("No data to display for the 'After' period.")

        else:
            st.error("Could not process the data after loading. Please check data format.")
    else:
        st.warning("Could not load data. Please check source configuration and availability.")

if __name__ == "__main__":
    main()
