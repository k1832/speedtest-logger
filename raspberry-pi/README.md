# Speedtest Logger to Google Sheets

This shell script (`speedtest.sh`) periodically runs an internet speed test, parses the results, and sends the data to a Google Apps Script web app, which can then log the results into a Google Sheet.

It's a simple way to track your internet connection's performance over time.

---

## How It Works

The script performs three main actions:

1.  **Runs Speed Test**: It uses the `speedtest` CLI to measure download speed, upload speed, and ping, outputting the results in JSON format.
2.  **Parses Data**: It uses `jq` to parse the JSON output and formats the key metrics into a single, comma-separated string: `timestamp,ping,download,upload`.
3.  **Posts Data**: It sends this data string in a JSON payload to a specified Google Apps Script Web App URL using `curl`.

---

## Dependencies

Before you can run this script, you need to have the following command-line tools installed:

* **`speedtest`**: The official Speedtest.net CLI.
    * *Installation*: Follow https://www.speedtest.net/ja/apps/cli
* **`jq`**: A lightweight and flexible command-line JSON processor.
    * *Installation (Ubuntu/Debian)*: `sudo apt-get install jq`
    * *Installation (macOS)*: `brew install jq`
* **`curl`**: A tool to transfer data from or to a server. It is usually pre-installed on most systems.

---

## Setup

1.  **Create a Google Apps Script Web App**:
    * Go to [script.google.com](https://script.google.com) and create a new project with a script that can receive a POST request and write data to a Google Sheet.
    * Deploy it as a **Web app**. When deploying, set **"Who has access"** to **"Anyone"**.
    * Copy the **Web app URL** provided after deployment. It will look like `https://script.google.com/macros/s/..../exec`.

2.  **Set the Environment Variable**:
    * The script requires an environment variable `SPEEDTEST_LOGGER_URL` to be set to your Google Apps Script Web App URL. You can set it in your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`) or just before running the script.
    * `export SPEEDTEST_LOGGER_URL="https://script.google.com/macros/s/YOUR_WEB_APP_ID/exec"`
    * Replace the URL with the one you copied in the previous step.

3.  **Make the Script Executable**:
    * Give the script execute permissions:
        ```bash
        chmod +x speedtest.sh
        ```

---

## Usage

Once the setup is complete, simply run the script from your terminal:

```bash
./speedtest.sh
````

### Automation with Cron

To automatically log your speed test results on a schedule, you can set up a cron job.

Open your crontab for editing:

```bash
crontab -e
```

Add a line to run the script at your desired interval. The example below runs the script every 10 minutes (at minutes 1, 11, 21, 31, 41, and 51 past the hour).

```bash
# Run speedtest logger every 10 minutes from minute 1 through 51
1-51/10 * * * * SPEEDTEST_LOGGER_URL="YOUR_URL" /path/to/your/speedtest.sh >> /path/to/your/speedtest.log 2>&1
```

  * `SPEEDTEST_LOGGER_URL="YOUR_URL"` sets the variable for the command. This is required for the script to work.
  * `/path/to/your/speedtest.sh` should be the absolute path to your script.
  * `>> /path/to/your/speedtest.log 2>&1` redirects all output (stdout and stderr) to a log file, which is useful for debugging.
