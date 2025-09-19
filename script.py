# 這是為 Google Colab 設計的 Python 腳本，用於執行 OCR。

# 步驟 1: 安裝必要的函式庫和 OCR 引擎。
!sudo apt-get install -y tesseract-ocr
!sudo apt-get install -y tesseract-ocr-chi-tra  # 安裝繁體中文語言包
!pip install pytesseract
!pip install Pillow
!pip install requests
!pip install gspread
!pip install google-auth
!pip install PyDrive2

# 步驟 2: 進行使用者認證。
from google.colab import auth
import gspread
from google.auth import default
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# 步驟 3: 設定您的 Google Drive 和 Google Sheets ID。
# 請將以下替換為您的資料夾和試算表 ID。
DRIVE_FOLDER_ID = '1s8JjeT2_nPY90BueQLjyozvd4oaD4tvx'
SPREADSHEET_ID = '1sZs2F3aVYsoXZWGCramI3c3-q3-YJcxFWAMGZgcW0Ag'

# 步驟 4: 下載圖片、執行 OCR 並將結果寫入 Google 試算表。
import requests
from PIL import Image
from datetime import datetime
import pytesseract
import io
import re

IMAGE_URL = "https://baci.168nana168.com/upload/%E6%9D%BF%E6%A9%8B_2505052_%E4%BF%83%E9%8A%B7%E5%90%8D%E5%96%AE/1.jpg"

def authenticate_and_save_to_drive():
    try:
        # 使用者認證
        auth.authenticate_user()
        gauth = GoogleAuth()
        gauth.credentials = auth.default()[0]
        drive = GoogleDrive(gauth)
        return drive
    except Exception as e:
        print(f"身份驗證或 Google Drive 連結發生錯誤：{e}")
        return None

try:
    # 下載圖片
    print("正在下載圖片...")
    response = requests.get(IMAGE_URL)
    response.raise_for_status()
    image_content = io.BytesIO(response.content)
    image_name = f"downloaded_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    # 將圖片存到雲端硬碟
    drive = authenticate_and_save_to_drive()
    if drive:
        print("正在將圖片存到 Google 雲端硬碟...")
        file = drive.CreateFile({'title': image_name, 'parents': [{'id': DRIVE_FOLDER_ID}]})
        file.SetContentFile(image_content.name)
        file.Upload()
        print("圖片已成功儲存至雲端硬碟！")

    # 執行 OCR
    print("正在執行 OCR...")
    image = Image.open(image_content)
    extracted_text = pytesseract.image_to_string(image, lang='chi_tra')
    print("OCR 完成。")

    # 處理文字
    # 定義要移除的關鍵詞和句子
    unwanted_phrases = [
        "消費只要1500", "一天最少更換兩輪名單", "促銷價+500立即開通VIP90天!!",
        "只要跟總機說加入會員!以下範例:", "網站上妹子原價2000直接-200再+500=2300",
        "即可獲得會員90天~", "來超過99次續會員可以得到永久vip"
    ]

    # 移除多餘的空白和換行
    text_lines = extracted_text.split('\n')
    cleaned_lines = []
    for line in text_lines:
        cleaned_line = line.strip()
        if cleaned_line and not any(phrase in cleaned_line for phrase in unwanted_phrases):
            cleaned_lines.append(cleaned_line)

    names = []
    for line in cleaned_lines:
        names.extend(line.split())

    if names:
        # 寫入 Google 試算表
        print("正在寫入 Google 試算表...")
        auth.authenticate_user()
        creds, _ = default()
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.get_worksheet(0) # 取得第一個工作表

        # 只將名單寫入 Google 試算表
        worksheet.append_row(names)

        print("\n辨識結果已成功寫入 Google 試算表！")
    else:
        print("辨識失敗：在圖片中找不到任何文字。")

except gspread.exceptions.APIError as e:
    print(f"Google Sheets API 發生錯誤，請檢查您的試算表 ID 和權限：{e}")
except Exception as e:
    print(f"執行時發生錯誤：{e}")
