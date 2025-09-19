import requests
from PIL import Image
from datetime import datetime
import pytesseract
import io
import gspread
from google.oauth2.service_account import Credentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# === 設定參數 ===
IMAGE_URL = "https://baci.168nana168.com/upload/%E6%9D%BF%E6%A9%8B_2505052_%E4%BF%83%E9%8A%B7%E5%90%8D%E5%96%AE/1.jpg"
SPREADSHEET_ID = "1sZs2F3aVYsoXZWGCramI3c3-q3-YJcxFWAMGZgcW0Ag"
DRIVE_FOLDER_ID = "你的Google雲端硬碟資料夾ID"  # 先到雲端硬碟建立資料夾，把 ID 換進來
SERVICE_ACCOUNT_FILE = "service_account.json"  # 下載的 JSON 憑證路徑


def authenticate_gspread():
    """連線 Google Sheet"""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc


def authenticate_drive():
    """連線 Google Drive"""
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(SERVICE_ACCOUNT_FILE)
    drive = GoogleDrive(gauth)
    return drive


def main():
    # === 下載圖片 ===
    print("正在下載圖片...")
    response = requests.get(IMAGE_URL)
    response.raise_for_status()
    image_content = io.BytesIO(response.content)
    image_name = f"downloaded_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    # === 上傳圖片到 Google Drive ===
    print("正在上傳圖片到 Google 雲端硬碟...")
    drive = authenticate_drive()
    file = drive.CreateFile({'title': image_name, 'parents': [{'id': DRIVE_FOLDER_ID}]})
    file.SetContentFile(image_name)  # 存成暫存檔再上傳
    with open(image_name, "wb") as f:
        f.write(image_content.getvalue())
    file.Upload()
    print("圖片已成功儲存至雲端硬碟！")

    # === OCR 辨識文字 ===
    print("正在執行 OCR...")
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
        worksheet = spreadsheet.get_worksheet(0)  # 取得第一個工作表
        worksheet.append_row(names)
        print("\n✅ 辨識結果已成功寫入 Google 試算表！")
    else:
        print("❌ 辨識失敗：在圖片中找不到任何文字。")


if __name__ == "__main__":
    main()
