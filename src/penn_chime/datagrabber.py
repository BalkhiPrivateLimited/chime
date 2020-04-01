import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

def fromSheet():
    credentials = ServiceAccountCredentials.from_json_keyfile_name("src/credentials.json", scopes=SCOPES)
    client = gspread.authorize(credentials)
    sheet = client.open("Covid-19").sheet1
    data = sheet.get_all_records()
    return data
