const SPRSHEET = SpreadsheetApp.getActiveSpreadsheet();
const SHEET_NAME = "2021";
const SHEET = SPRSHEET.getSheetByName(SHEET_NAME);

function doPost(e) {
    const body = JSON.parse(e.postData.contents);
    console.log({body});
    const dataArray = body.data.split(',');
    console.log({dataArray});
    if (dataArray.length != 4) {
      const message = "Posted data is invalid.\n";
      console.log(message);
      return ContentService.createTextOutput(message);
    }
    const [timestamp, ping, download, upload] = dataArray;

    const ROW_TO_INSERT = 2;
    SHEET.insertRowBefore(ROW_TO_INSERT);
    SHEET.getRange(ROW_TO_INSERT, 1).setValue(timestamp);
    SHEET.getRange(ROW_TO_INSERT, 2).setValue(ping);
    SHEET.getRange(ROW_TO_INSERT, 3).setValue(download);
    SHEET.getRange(ROW_TO_INSERT, 4).setValue(upload);

    const ret_message = `timestamp: ${timestamp}, ping: ${ping}, download: ${download}, upload: ${upload}\n`;
    return ContentService.createTextOutput(ret_message);
}
