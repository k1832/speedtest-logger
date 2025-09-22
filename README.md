# speedtest-logger
## ログの例
```
timestamp (UTC),ping (ms),download (Mbps),upload (Mbps)
2025-09-22T07:41:28Z,4.318,73.684,42.020
2025-09-22T07:36:16Z,3.904,75.723,58.294
2025-09-22T07:34:06Z,4.102,81.757,37.344
2025-09-22T07:33:19Z,4.147,77.769,58.052
2025-09-22T07:25:26Z,7.231,53.543,42.644
2025-09-22T07:18:48Z,3.983,56.417,44.239
2025-09-22T07:06:21Z,3.603,59.414,39.988
```
## ラズパイ側の挙動
シェルスクリプトで「スピードテスト→Google Apps ScriptにPOST」までする。cronでシェルスクリプトを定期実行。   
### シェルスクリプト
1. **speedtest-cli** を走らせる
2. データを切って **Google Apps Script** で書いたエンドポイントを叩く  

### cron設定
`1-51/10 * * * * /path/to/script/speedtest.sh`  

### 工夫点
- 00分と30分のテストがなぜかこけるので1分ずらしている  
- cron実行環境では環境変数が読み込まれないため、シェルスクリプトの一行目で読み込みのためのオプションを追加  
参考: [cron実行時の環境変数を設定](https://admnote.paix.jp/2014/07/cron%E5%AE%9F%E8%A1%8C%E6%99%82%E3%81%AE%E7%92%B0%E5%A2%83%E5%A4%89%E6%95%B0%E3%82%92%E8%A8%AD%E5%AE%9A/)  

## Google Apps Script側の挙動
1. ラズパイから受け取ったデータをスプレッドシートに書き込む  

## Raspberry Piの省電力化
### Change the CPU governor for more agressive power saving
`echo powersave | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`

### Disable unused hardware

Open `sudo vim /boot/firmware/config.txt`, then add the following lines:
```
# Disable HDMI
hdmi_blanking=2

# Disable Wi-Fi and Bluetooth
dtoverlay=disable-wifi
dtoverlay=disable-bt
```

### Measure CPU temperature
`vcgencmd measure_temp`
