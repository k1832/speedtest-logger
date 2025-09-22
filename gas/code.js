const SPRSHEET = SpreadsheetApp.getActiveSpreadsheet();
const SHEET_NAME = "2025";
const SHEET = SPRSHEET.getSheetByName(SHEET_NAME);

function doPost(e) {
  const json = JSON.parse(e.postData.contents);
  console.log({json});

  const ROW_TO_INSERT = 2;
  SHEET.insertRowBefore(ROW_TO_INSERT);
  SHEET.getRange(ROW_TO_INSERT, 1).setValue(json.timestamp);
  SHEET.getRange(ROW_TO_INSERT, 2).setValue(json.ping);
  SHEET.getRange(ROW_TO_INSERT, 3).setValue(json.download);
  SHEET.getRange(ROW_TO_INSERT, 4).setValue(json.upload);

  return ContentService.createTextOutput("success");
}
