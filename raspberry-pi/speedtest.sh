#!/bin/bash -l

# speedtest
json_result=`speedtest-cli --json`
echo $json_result

# parse result
timestamp=`echo $json_result | jq -r ".timestamp"`
ping=`echo $json_result | jq -r ".ping"`
download=`echo $json_result | jq -r ".download"`
upload=`echo $json_result | jq -r ".upload"`
echo $timestamp
echo $ping
echo $download
echo $upload
result="$timestamp,$ping,$download,$upload"

# post to google apps script
# SPEEDTEST_LOGGER_URL (web app URL of Google Apps Script) should be set in bash
# SPEEDTEST_LOGGER_URL=https://script.google.com/macros/s/xxx/exec
json="'{\"data\": \"$result\"}'"
eval "curl --data ${json} --header 'Content-Type: application/json' -L $SPEEDTEST_LOGGER_URL"
