#!/bin/bash

echo "Running speedtest..."

json_result=$(speedtest --format json)

if [ -z "$json_result" ]; then
  echo "Error: speedtest command failed or returned an empty result."
  exit 1
fi

# Construct a new JSON to upload (also convert bps -> Mbps)
parsed_json=$(echo "$json_result" | jq '{ timestamp: .timestamp, ping: .ping.latency, download: (.download.bandwidth / 1000000), upload: (.upload.bandwidth / 1000000) }')

echo "---"
echo "Prepared JSON for upload:"
echo "$parsed_json"
echo "---"

# Post to google apps script
# SPEEDTEST_LOGGER_URL (web app URL of Google Apps Script) should be set in bash
# SPEEDTEST_LOGGER_URL=https://script.google.com/macros/s/xxx/exec
curl -X POST \
  -H "Content-Type: application/json" \
  -d "$parsed_json" \
  "$SPEEDTEST_LOGGER_URL" > /dev/null 2>&1

echo -e "\n\nUpload command finished."
