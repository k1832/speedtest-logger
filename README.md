# speedtest-logger
## 実際のログ（現在非公開）
https://docs.google.com/spreadsheets/d/11nWYSUnr6VswYhoDquz1GJVZFRifad-XMFQA9ZyUJn8/edit?usp=sharing  
## ラズパイ側の挙動
シェルスクリプトで「スピードテスト→Google Apps ScriptにPOST」までする。cronでシェルスクリプトを定期実行。   
### シェルスクリプト
1. **speedtest-cli** を走らせる
2. データを切って **Google Apps Script** で書いたエンドポイントを叩く  

### cron設定
`1-51/10 * * * * /path/to/script/speedtest.sh`  

※注意  
1. 00分と30分のテストがなぜかこけるので1分ずらしている  
2. cronで実行される時ほとんどの環境変数が読み込まれないため工夫が必要  
参考: [cron実行時の環境変数を設定](https://admnote.paix.jp/2014/07/cron%E5%AE%9F%E8%A1%8C%E6%99%82%E3%81%AE%E7%92%B0%E5%A2%83%E5%A4%89%E6%95%B0%E3%82%92%E8%A8%AD%E5%AE%9A/)  

## Google Apps Script側の挙動
1. ラズパイから受け取ったデータをスプレッドシートに書き込む  
