import requests
from PIL import Image
from datetime import datetime
import pytesseract
import io
import gspread
import json
with open("service_account.json") as f:
    data = f.read()
    print("Service Account JSON Preview:", data[:200])  # 只印前200字
    json.loads(data)  # 驗證 JSON 格式
    
from google.oauth2.service_account import Credentials

# 設定參數
IMAGE_URL = "https://baci.168nana168.com/upload/%E6%9D%BF%E6%A9%8B_2505052_%E4%BF%83%E9%8A%B7%E5%90%8D%E5%96%AE/1.jpg"
SPREADSHEET_ID = "你的試算表ID"

def main():
    # 下載圖片
    print("Downloading image...")
    response = requests.get(IMAGE_URL)
    image = Image.open(io.BytesIO(response.content))

    # OCR
    print("Running OCR...")
    text = pytesseract.image_to_string(image, lang="chi_tra")
    print("OCR Result:", text)

    # Google Sheets 寫入
    print("Writing to Google Sheet...")
    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)
    worksheet = gc.open_by_key(SPREADSHEET_ID).sheet1
    worksheet.append_row([datetime.now().isoformat(), text])
    print("Done!")

if __name__ == "__main__":
    main()
