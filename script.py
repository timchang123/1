import requests
from PIL import Image
from datetime import datetime
import pytesseract
import io

import gspread
from google.oauth2.service_account import Credentials

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# === 設定參數 ===
IMAGE_URL = "https://baci.168nana168.com/upload/%E6%9D%BF%E6%A9%8B_2505052_%E4%BF%83%E9%8A%B7%E5%90%8D%E5%96%AE/1.jpg"
SPREADSHEET_ID = "1sZs2F3aVYsoXZWGCramI3c3-q3-YJcxFWAMGZgcW0Ag"
SHARED_DRIVE_FOLDER_ID = "1s8JjeT2_nPY90BueQLjyozvd4oaD4tvx"
SERVICE_ACCOUNT_FILE = "service_account.json"


def authenticate_gspread():
    """連線 Google Sheet"""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc


def upload_to_drive(image_content, image_name):
    """上傳圖片到 Google Drive (Shared Drive)"""
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": image_name,
        "parents": [SHARED_DRIVE_FOLDER_ID],
    }

    # 確保 image_content 是 BytesIO，重設游標
    image_content.seek(0)
    media = MediaIoBaseUpload(image_content, mimetype="image/jpeg")

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
        supportsAllDrives=True
    ).execute()

    print("✅ 上傳成功，檔案 ID:", file.get("id"))


def main():
    # === 下載圖片 ===
    print("正在下載圖片...")
    response = requests.get(IMAGE_URL)
    response.raise_for_status()
    image_content = io.BytesIO(response.content)
    image_name = f"downloaded_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    # === 上傳到 Google Drive ===
    print("正在上傳圖片到 Google Drive...")
    upload_to_drive(image_content, image_name)

    # === OCR 辨識文字 ===
    print("正在執行 OCR...")
    image_content.seek(0)  # OCR 前要重設游標
    image = Image.open(image_content)
    extracted_text = pytesseract.image_to_string(image, lang="chi_tra")
    print("OCR 完成。")

    # === 清理文字 ===
    unwanted_phrases = [
        "消費只要1500", "一天最少更換兩輪名單", "促銷價+500立即開通VIP90天!!",
        "只要跟總機說加入會員!以下範例:", "網站上妹子原價2000直接-200再+500=2300",
        "即可獲得會員90天~", "來超過99次續會員可以得到永久vip"
    ]

    text_lines = extracted_text.split("\n")
    cleaned_lines = []
    for line in text_lines:
        cleaned_line = line.strip()
        if cleaned_line and not any(phrase in cleaned_line for phrase in unwanted_phrases):
            cleaned_lines.append(cleaned_line)

    names = []
    for line in cleaned_lines:
        names.extend(line.split())

    # === 寫入 Google Sheet ===
    if names:
        print("正在寫入 Google 試算表...")
        gc = authenticate_gspread()
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.get_worksheet(0)
        worksheet.append_row(names)
        print("\n✅ 辨識結果已成功寫入 Google 試算表！")
    else:
        print("❌ 辨識失敗：在圖片中找不到任何文字。")


if __name__ == "__main__":
    main()
