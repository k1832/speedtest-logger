Of course. Here is the updated `README.md` that includes the latest analysis features for identifying hourly patterns and the slowest specific time intervals.

-----

# 📊 Internet Speed Test Analyzer

A Python script to analyze and visualize internet speed test data from a CSV file. It identifies the slowest connection intervals, summarizes performance by hour of day, and generates detailed plots.

-----

## ⚙️ Setup

1.  **Install dependencies**:
    ```bash
    pip install pandas matplotlib
    ```
2.  **Place your data file** (`speedtest-log.csv`) in the same directory as the script.

-----

## ▶️ Usage

Run the script from your terminal.

  * **To save the plots as PNG files**:
    ```bash
    python analyze_speedtest.py
    ```
  * **To display interactive plot windows**:
    ```bash
    python analyze_speedtest.py --output show
    ```
  * **To specify a different CSV file**:
    ```bash
    python analyze_speedtest.py --file "path/to/your/data.csv"
    ```

-----

## 📋 Example Output

### Console

The script prints several summaries to your terminal: a "Top 10" list of the slowest intervals, an hourly performance breakdown, and overall statistics.

```
--- 🎯 Top 10 Slowest 15-Minute Intervals ---
                     Ping Latency  Download Speed (Mbps)  Upload Speed (Mbps)
Timestamp
2021-10-02 11:30:00          23.0              78.082035           143.149958
2021-12-05 06:15:00          18.0              83.136456            21.932975
2021-10-17 10:15:00          18.0              85.645999           128.971201
... (and so on)
-------------------------------------------

--- Average Performance by Hour ---
      Download Speed (Mbps)  Upload Speed (Mbps)  Ping Latency
Hour
0                  145.451368           169.354378     19.533333
1                  146.544254           164.444772     20.200000
2                  144.333202           171.011488     19.428571
... (and so on)
-------------------------------------

--- Overall Performance Statistics ---
       Ping Latency  Download Speed (Mbps)  Upload Speed (Mbps)
count    356.000000             356.000000           356.000000
mean      20.112360             141.082531           159.261825
std        3.511529              16.294711            41.258169
min       15.000000              78.082035            21.932975
... (and so on)
```

### Generated Files (`--output save`)

The script will generate three image files:

1.  **`internet_performance_over_time.png`**: A line graph showing your ping, download, and upload measurements over the entire time period.
2.  **`internet_speed_distributions.png`**: A set of three histograms showing the frequency of different values for your ping, download, and upload speeds.
3.  **`hourly_performance.png`**: A bar chart showing the average internet speed and latency for each hour of the day, helping you to easily spot daily patterns.
