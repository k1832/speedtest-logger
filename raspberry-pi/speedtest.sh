#!/bin/bash -l

# speedtest
json_result=`speedtest-cli --json`
echo JSON result: $json_result

# parse result
result=`echo $json_result | jq -r '.timestamp + "," + (.ping|tostring) + "," + (.download|tostring) + "," + (.upload|tostring)'`
echo Parsed result: $result

# post to google apps script
# SPEEDTEST_LOGGER_URL (web app URL of Google Apps Script) should be set in bash
# SPEEDTEST_LOGGER_URL=https://script.google.com/macros/s/xxx/exec
json="'{\"data\": \"$result\"}'"
eval "curl --data ${json} --header 'Content-Type: application/json' -L $SPEEDTEST_LOGGER_URL"
