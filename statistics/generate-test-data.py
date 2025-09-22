import csv
import random
from datetime import datetime, timedelta

# --- CONFIGURATION ---
OUTPUT_FILE = "generated-speed-test-data.csv"
START_DATE = datetime(2025, 8, 22, 0, 0, 0)
NUMBER_OF_DAYS = 30
TIME_INTERVAL_MINUTES = 5

# Data generation parameters
PING_MEAN = 4.5
PING_STD_DEV = 1.5
DOWNLOAD_MIN_MBPS = 30.0
DOWNLOAD_MAX_MBPS = 95.0
UPLOAD_MIN_MBPS = 25.0
UPLOAD_MAX_MBPS = 70.0

# Chance of an outlier ping (e.g., a network spike)
OUTLIER_PING_CHANCE = 0.01  # 1% chance
OUTLIER_PING_MIN = 20.0
OUTLIER_PING_MAX = 150.0
# --- END OF CONFIGURATION ---


def generate_test_data():
    """Generates and writes the speed test data to a CSV file."""
    end_date = START_DATE + timedelta(days=NUMBER_OF_DAYS)
    current_time = START_DATE

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        # Write the header row
        writer.writerow(
            ["timestamp (UTC)", "ping (ms)", "download (Mbps)", "upload (Mbps)", "comment"]
        )

        while current_time < end_date:
            # Add some randomness to the time interval to make it more realistic
            time_jitter_seconds = random.randint(-60, 60)
            current_time += timedelta(
                minutes=TIME_INTERVAL_MINUTES, seconds=time_jitter_seconds
            )

            # Generate ping
            if random.random() < OUTLIER_PING_CHANCE:
                ping = round(random.uniform(OUTLIER_PING_MIN, OUTLIER_PING_MAX), 3)
            else:
                ping = round(abs(random.normalvariate(PING_MEAN, PING_STD_DEV)), 3)

            # Generate download and upload speeds
            download = round(
                random.uniform(DOWNLOAD_MIN_MBPS, DOWNLOAD_MAX_MBPS), 3
            )
            upload = round(random.uniform(UPLOAD_MIN_MBPS, UPLOAD_MAX_MBPS), 3)

            # Format timestamp to match the example (ISO 8601 format with 'Z')
            timestamp_str = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Write the data row
            writer.writerow([timestamp_str, ping, download, upload, ""])

    print(f"Successfully generated test data in '{OUTPUT_FILE}'")


if __name__ == "__main__":
    generate_test_data()
