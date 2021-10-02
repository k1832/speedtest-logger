import csv
import os
import datetime

if __name__ == "__main__":
    base_path: str = os.path.dirname(os.path.abspath(__file__))
    data_dir_path: str = os.path.join(base_path, "data")
    
    for file_name in os.listdir(data_dir_path):
        if not file_name.endswith(".csv"):
            continue
        full_path: str = os.path.join(data_dir_path, file_name)
        with open(full_path) as f:
            reader = csv.reader(f)
            # ignore the header
            data = [row for row in reader][1:]
        failures = 0
        for line in data:
            try:
                time_in_utc = datetime.datetime.fromisoformat(line[0][:-1])
                time_in_jst = time_in_utc + datetime.timedelta(hours=9)
            except:
                failures += 1
                print(f"Parse failed: {line}")
        print(f"Total failures: {failures}")
