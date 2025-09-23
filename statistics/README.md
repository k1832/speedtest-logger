# 📊 Internet Speed Test Dashboard

An interactive web dashboard built with **Streamlit** to analyze and visualize internet speed test data. This application can pull data live from a **Google Sheet** or use a **local CSV file** for analysis, providing a comprehensive overview of your internet performance.

-----

## ✨ Features

  * **Dual Data Sources**: Seamlessly switch between fetching live data from Google Sheets and using a local CSV file for testing.
  * **Time Series Analysis**: View download, upload, and ping metrics over time to spot trends.
  * **Hourly & Daily Patterns**: Analyze average performance by hour of the day and day of the week to identify peak times or recurring slowdowns.
  * **Weekday vs. Weekend Comparison**: Compare performance trends between weekdays and weekends using line charts and heatmaps.
  * **Distributions & Correlations**: Understand the statistical distribution of your speeds and see how the different metrics relate to each other.
  * **Interactive UI**: A clean, web-based interface that requires no command-line arguments to run.

-----

## ⚙️ Setup

Follow these steps to get the dashboard running on your local machine.

### 1\. Clone the Repository & Install Dependencies

First, clone the project and install the required Python libraries from `requirements.txt`.

```bash
# It's recommended to use a virtual environment
python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`

pip install -r requirements.txt
```

### 2\. Configure Your Data Source

You can use a local CSV file or connect to a Google Sheet.

#### **Option A: Local CSV File (for quick testing)**

1.  Create a folder named `data` in the root of your project directory.
2.  Place your speedtest log file inside it and name it `speedtest-log.csv`.

#### **Option B: Google Sheets (for live data)**

1.  **Enable Google APIs**: Go to the [Google Cloud Console](https://console.cloud.google.com/), create a project, and enable the **Google Drive API** and **Google Sheets API**.

2.  **Create a Service Account**: In the "Credentials" section, create a service account, generate a **JSON key**, and download it.

3.  **Share Your Sheet**: Open the downloaded JSON key and find the `client_email`. Share your Google Sheet with this email address, giving it at least "Viewer" permissions.

4.  **Create a Secrets File**:

      * In your project directory, create a new folder: `.streamlit`.
      * Inside `.streamlit`, create a file named `secrets.toml`.
      * Copy the entire content of the downloaded JSON key file and paste it into `secrets.toml` under the `[gcp_service_account]` heading. It should look like this:

    <!-- end list -->

    ```toml
    [gcp_service_account]
    type = "service_account"
    project_id = "your-gcp-project-id"
    private_key_id = "your-private-key-id"
    private_key = "-----BEGIN PRIVATE KEY-----\n...your-private-key...\n-----END PRIVATE KEY-----\n"
    client_email = "your-service-account-email@...gserviceaccount.com"
    client_id = "your-client-id"
    # ... and so on for all fields in the JSON file
    ```

-----

## ▶️ Running the Dashboard

Once the setup is complete, run the application from your terminal:

```bash
streamlit run dashboard.py
```

Your web browser will automatically open with the dashboard.

-----

## 🚀 Using the Dashboard

The dashboard will load and display all the analysis plots.

  * **Switching Data Sources**: Use the toggle switch in the sidebar to alternate between loading data from your **local CSV file** and fetching live data from **Google Sheets**.

-----

## 📁 Project Structure

Ensure your project files are organized as follows for the script to work correctly:

```
.
├── .streamlit/
│   └── secrets.toml    # For Google Sheets credentials (DO NOT COMMIT TO GIT)
├── data/
│   └── speedtest-log.csv # Your local CSV data
├── dashboard.py          # The main Streamlit application script
└── requirements.txt      # Project dependencies
```
