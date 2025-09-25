import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import gspread
from google.oauth2.service_account import Credentials
import os

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

def display_realtime_comparison(df: pd.DataFrame):
    """Calculates and displays the last X mins average vs. historical average."""

    realtime_window = 30
    st.header(f"⏱️ Last {realtime_window} mins Performance vs. Historical Norm")

    now = pd.Timestamp.now(tz='Asia/Tokyo')
    time_ago = now - pd.Timedelta(minutes=realtime_window)
    recent_data = df[df.index >= time_ago]

    if recent_data.empty:
        st.warning(f"No speedtest data recorded in the last {realtime_window} minutes.")
        return

    recent_avg = recent_data[['download_mbps', 'upload_mbps', 'ping']].mean()
    current_day = now.day_name()
    current_time_window = (time_ago.time(), now.time())

    historical_data = df[(df['day_of_week'] == current_day) & (df.index < time_ago)]
    # Convert index to a Series to use the .dt accessor, which the editor's linter understands
    historical_times = historical_data.index.to_series().dt.time
    historical_match = historical_data[
        (historical_times >= current_time_window[0]) &
        (historical_times <= current_time_window[1])
    ]

    if historical_match.empty:
        st.info(f"Not enough historical data for this time slot on a {current_day} to make a comparison.")
        return

    historical_avg = historical_match[['download_mbps', 'upload_mbps', 'ping']].mean()

    def calculate_delta(current, historical):
        if historical == 0: return 0
        return ((current - historical) / historical) * 100

    delta_dl = calculate_delta(recent_avg['download_mbps'], historical_avg['download_mbps'])
    delta_ul = calculate_delta(recent_avg['upload_mbps'], historical_avg['upload_mbps'])
    delta_ping = calculate_delta(recent_avg['ping'], historical_avg['ping'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label=f"Download (vs. typical {current_day})",
            value=f"{recent_avg['download_mbps']:.1f} Mbps",
            delta=f"{delta_dl:.1f}%",
            delta_color="normal"
        )
    with col2:
        st.metric(
            label=f"Upload (vs. typical {current_day})",
            value=f"{recent_avg['upload_mbps']:.1f} Mbps",
            delta=f"{delta_ul:.1f}%",
            delta_color="normal"
        )
    with col3:
        st.metric(
            label=f"Ping (vs. typical {current_day})",
            value=f"{recent_avg['ping']:.1f} ms",
            delta=f"{delta_ping:.1f}%",
            delta_color="inverse"  # Lower ping is better, so we invert the color
        )

def plot_performance_over_time(df: pd.DataFrame):
    st.header("📈 Performance Over Time")
    # Using constrained_layout=True is great
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True, constrained_layout=True)
    fig.suptitle('Internet Performance Over Time (JST)')

    sns.lineplot(data=df, x=df.index, y='download_mbps', ax=axes[0], color='blue')
    axes[0].set(title='Download Speed Over Time', ylabel='Download Speed\n(Mbps)')
    axes[0].grid(True)

    sns.lineplot(data=df, x=df.index, y='upload_mbps', ax=axes[1], color='green')
    axes[1].set(title='Upload Speed Over Time', ylabel='Upload Speed\n(Mbps)')
    axes[1].grid(True)

    sns.lineplot(data=df, x=df.index, y='ping', ax=axes[2], color='red')
    axes[2].set(title='Ping Latency Over Time', ylabel='Ping\n(ms)', xlabel='Date and Time (JST)')
    axes[2].grid(True)

    fig.autofmt_xdate()

    st.pyplot(fig)

def plot_performance_by_hour(df: pd.DataFrame):
    st.header("🕔 Performance by Hour of Day")
    hourly_stats = df.groupby('hour')[['download_mbps', 'upload_mbps', 'ping']].mean()
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True, constrained_layout=True)
    fig.suptitle('Average Performance by Hour of Day (JST)')

    sns.barplot(data=hourly_stats, x=hourly_stats.index, y='download_mbps', ax=axes[0])
    axes[0].set(title='Average Download Speed by Hour', ylabel='Avg. Download Speed (Mbps)')

    sns.barplot(data=hourly_stats, x=hourly_stats.index, y='upload_mbps', ax=axes[1])
    axes[1].set(title='Average Upload Speed by Hour', ylabel='Avg. Upload Speed (Mbps)')

    sns.barplot(data=hourly_stats, x=hourly_stats.index, y='ping', ax=axes[2])
    axes[2].set(title='Average Ping Latency by Hour', ylabel='Avg. Ping (ms)', xlabel='Hour of Day (0-23)')

    st.pyplot(fig)

def plot_performance_by_day_of_week(df: pd.DataFrame):
    st.header("🗓️ Performance by Day of Week")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_stats = df.groupby('day_of_week')[['download_mbps', 'upload_mbps', 'ping']].mean().reindex(day_order)
    fig, axes = plt.subplots(1, 3, figsize=(12, 5), constrained_layout=True)
    fig.suptitle('Average Performance by Day of Week (JST)')

    metrics = ['download_mbps', 'upload_mbps', 'ping']
    titles = ['Download Speed (Mbps)', 'Upload Speed (Mbps)', 'Ping (ms)']
    for i, (metric, title) in enumerate(zip(metrics, titles)):
        sns.barplot(data=daily_stats, x=daily_stats.index, y=metric, ax=axes[i])
        axes[i].set_title(f"Average {title}\nby Day")
        axes[i].set_ylabel(f"Average {title}")
        axes[i].set_xlabel("")
        axes[i].tick_params(axis='x', rotation=45)

    st.pyplot(fig)

def plot_distributions_and_correlation(df: pd.DataFrame):
    st.header("🧑‍🤝‍🧑 Correlations and Distributions")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Correlation Matrix")
        fig1, ax1 = plt.subplots(figsize=(6, 5), constrained_layout=True)
        sns.heatmap(df[['ping', 'download_mbps', 'upload_mbps']].corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax1)
        st.pyplot(fig1)

    with col2:
        st.subheader("Metric Distributions")
        fig2, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)
        sns.histplot(data=df, x='download_mbps', kde=True, ax=axes[0], color='skyblue').set_title('Download')
        sns.histplot(data=df, x='upload_mbps', kde=True, ax=axes[1], color='olive').set_title('Upload')
        sns.histplot(data=df, x='ping', kde=True, ax=axes[2], color='gold').set_title('Ping')
        st.pyplot(fig2)

def plot_weekday_vs_weekend_performance(df: pd.DataFrame):
    st.header("👨‍💻 Weekday vs. Weekend Performance")
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
    heatmap_data = cross_stats.pivot(index='day_type', columns='hour', values='download_mbps')
    fig2, ax2 = plt.subplots(figsize=(12, 2), constrained_layout=True)
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="rocket_r", linewidths=.5, ax=ax2)
    ax2.set(title='Average Download Speed (Mbps) by Hour and Day Type', xlabel='Hour of Day (JST)', ylabel='')
    st.pyplot(fig2)

def main():
    """Main function to build and run the Streamlit app."""
    st.set_page_config(page_title="Speedtest Dashboard", layout="wide")

    if st.secrets.get("local", False):
        st.sidebar.header("⚙️ Data Source Configuration")
        use_local = st.sidebar.toggle("Use Local CSV", help="If on, loads data from local CSV. If off, fetches from Google Sheets.")
    else:
        use_local = False

    st.title("📊 Internet Speedtest Analysis Dashboard")
    st.markdown("This dashboard analyzes internet performance metrics logged over time.")
    raw_df = load_data(use_local_csv=use_local)
    if raw_df is not None:
        processed_df = prepare_data(raw_df)
        if processed_df is not None:
            display_realtime_comparison(processed_df)
            st.header("🔢 Data Overview & Statistics")
            st.dataframe(processed_df[['ping', 'download_mbps', 'upload_mbps']].describe())
            plot_performance_over_time(processed_df)
            plot_weekday_vs_weekend_performance(processed_df)
            plot_performance_by_hour(processed_df)
            plot_performance_by_day_of_week(processed_df)
            plot_distributions_and_correlation(processed_df)
        else:
            st.error("Could not process the data after loading. Please check data format.")
    else:
        st.warning("Could not load data. Please check source configuration and availability.")

if __name__ == "__main__":
    main()
