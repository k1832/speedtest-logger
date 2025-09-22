import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import gspread
from google.oauth2.service_account import Credentials
import os # Added for handling file paths

# --- 1. UNIFIED DATA LOADING (LOCAL CSV OR GOOGLE SHEETS) ---

@st.cache_data(ttl=600)  # Cache remains effective for both sources
def load_data(use_local_csv: bool) -> pd.DataFrame | None:
    """Loads data from a local CSV file or Google Sheets based on the toggle."""
    if use_local_csv:
        # --- LOAD FROM LOCAL CSV ---
        st.info(" sourcing data from local CSV file...")

        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, "data", "generated_speed_test_data.csv")
        try:
            # Assumes the CSV is in a 'data' subfolder
            # You can change 'data/speedtest-log.csv' to your file's path
            df = pd.read_csv(file_path)
            st.success("✅ Successfully loaded data from local CSV.")
            return df
        except FileNotFoundError:
            st.error(f"❌ ERROR: Local file not found at '{file_path}'. Please check the path.")
            return None
        except Exception as e:
            st.error(f"❌ An error occurred while reading the local CSV file: {e}")
            return None
    else:
        # --- LOAD FROM GOOGLE SHEETS ---
        st.info(" sourcing data from Google Sheets...")
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

# --- 2. DATA PREPARATION (No changes needed here) ---

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

    df.set_index(pd.to_datetime(df['timestamp_utc']).dt.tz_convert('Asia/Tokyo'), inplace=True)
    df.index.name = 'timestamp_jst'
    df['hour'] = df.index.hour
    df['day_of_week'] = df.index.day_name()
    df['day_type'] = df.index.to_series().apply(lambda x: 'Weekday' if x.dayofweek < 5 else 'Weekend')

    return df

# --- 3. PLOTTING FUNCTIONS (No changes needed here) ---
# ... (All your plotting functions like plot_performance_over_time, etc., remain exactly the same) ...

def plot_performance_over_time(df: pd.DataFrame):
    st.header("📈 Performance Over Time")
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
    st.pyplot(fig)

def plot_performance_by_hour(df: pd.DataFrame):
    st.header("🕔 Performance by Hour of Day")
    hourly_stats = df.groupby('hour')[['download_mbps', 'upload_mbps', 'ping']].mean()
    fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=True)
    fig.suptitle('Average Performance by Hour of Day (JST)', fontsize=16)

    sns.barplot(data=hourly_stats, x=hourly_stats.index, y='download_mbps', ax=axes[0], hue=hourly_stats.index, palette='viridis', legend=False)
    axes[0].set(title='Average Download Speed by Hour', ylabel='Avg. Download Speed (Mbps)')

    sns.barplot(data=hourly_stats, x=hourly_stats.index, y='upload_mbps', ax=axes[1], hue=hourly_stats.index, palette='plasma', legend=False)
    axes[1].set(title='Average Upload Speed by Hour', ylabel='Avg. Upload Speed (Mbps)')

    sns.barplot(data=hourly_stats, x=hourly_stats.index, y='ping', ax=axes[2], hue=hourly_stats.index, palette='magma', legend=False)
    axes[2].set(title='Average Ping Latency by Hour', ylabel='Avg. Ping (ms)', xlabel='Hour of Day (0-23)')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    st.pyplot(fig)

def plot_performance_by_day_of_week(df: pd.DataFrame):
    st.header("🗓️ Performance by Day of Week")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_stats = df.groupby('day_of_week')[['download_mbps', 'upload_mbps', 'ping']].mean().reindex(day_order)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Average Performance by Day of Week (JST)', fontsize=16)

    metrics = ['download_mbps', 'upload_mbps', 'ping']
    titles = ['Download Speed (Mbps)', 'Upload Speed (Mbps)', 'Ping (ms)']
    for i, (metric, title) in enumerate(zip(metrics, titles)):
        sns.barplot(data=daily_stats, x=daily_stats.index, y=metric, ax=axes[i], hue=daily_stats.index, palette='plasma', legend=False)
        axes[i].set_title(f"Average {title} by Day")
        axes[i].set_ylabel(f"Average {title}")
        axes[i].set_xlabel("")
        axes[i].tick_params(axis='x', rotation=45)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    st.pyplot(fig)

def plot_distributions_and_correlation(df: pd.DataFrame):
    st.header("🧑‍🤝‍🧑 Correlations and Distributions")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Correlation Matrix")
        fig1, ax1 = plt.subplots(figsize=(7, 6))
        sns.heatmap(df[['ping', 'download_mbps', 'upload_mbps']].corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax1)
        st.pyplot(fig1)

    with col2:
        st.subheader("Metric Distributions")
        fig2, axes = plt.subplots(1, 3, figsize=(15, 5))
        sns.histplot(data=df, x='download_mbps', kde=True, ax=axes[0], color='skyblue').set_title('Download')
        sns.histplot(data=df, x='upload_mbps', kde=True, ax=axes[1], color='olive').set_title('Upload')
        sns.histplot(data=df, x='ping', kde=True, ax=axes[2], color='gold').set_title('Ping')
        plt.tight_layout()
        st.pyplot(fig2)

def plot_weekday_vs_weekend_performance(df: pd.DataFrame):
    st.header("👨‍💻 Weekday vs. Weekend Performance")
    cross_stats = df.groupby(['day_type', 'hour'])[['download_mbps', 'ping']].mean().reset_index()

    fig1, axes = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    fig1.suptitle('Weekday vs. Weekend Performance by Hour', fontsize=16)
    sns.lineplot(data=cross_stats, x='hour', y='download_mbps', hue='day_type', ax=axes[0], marker='o')
    axes[0].set(title='Average Download Speed', ylabel='Download Speed (Mbps)')
    axes[0].grid(True)
    sns.lineplot(data=cross_stats, x='hour', y='ping', hue='day_type', ax=axes[1], marker='o')
    axes[1].set(title='Average Ping Latency', ylabel='Ping (ms)', xlabel='Hour of Day (JST)')
    axes[1].grid(True)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    st.pyplot(fig1)

    st.subheader("Download Speed Heatmap (Mbps)")
    heatmap_data = cross_stats.pivot(index='day_type', columns='hour', values='download_mbps')
    fig2, ax2 = plt.subplots(figsize=(16, 3))
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="rocket_r", linewidths=.5, ax=ax2)
    ax2.set_title('Average Download Speed (Mbps) by Hour and Day Type')
    ax2.set_xlabel('Hour of Day (JST)')
    ax2.set_ylabel('')
    st.pyplot(fig2)

# --- 4. MAIN STREAMLIT APP LOGIC (Modified) ---

def main():
    """Main function to build and run the Streamlit app."""
    st.set_page_config(page_title="Speedtest Dashboard", layout="wide")

    # --- Sidebar for data source selection ---
    st.sidebar.header("⚙️ Data Source Configuration")
    use_local = st.sidebar.toggle(
        "Use Local CSV File",
        value=True,
        help="If on, data will be loaded from `data/speedtest-log.csv`. If off, data will be fetched from Google Sheets."
    )

    st.title("📊 Internet Speedtest Analysis Dashboard")
    st.markdown("This dashboard analyzes internet performance metrics. Use the sidebar to switch data sources.")

    # --- Load data based on the toggle's state ---
    raw_df = load_data(use_local_csv=use_local)

    if raw_df is not None:
        processed_df = prepare_data(raw_df)

        if processed_df is not None:
            st.header("🔢 Data Overview & Statistics")
            st.dataframe(processed_df[['ping', 'download_mbps', 'upload_mbps']].describe())

            # Call all your plotting functions
            plot_performance_over_time(processed_df)
            plot_weekday_vs_weekend_performance(processed_df)
            plot_performance_by_hour(processed_df)
            plot_performance_by_day_of_week(processed_df)
            plot_distributions_and_correlation(processed_df)
        else:
            st.error("Could not process the data after loading. Please check the data format.")
    else:
        st.warning("Could not load data. Please check the source configuration and file/sheet availability.")

if __name__ == "__main__":
    main()
