import datetime

# 生成結果檔案
now = datetime.datetime.utcnow()
with open("output.txt", "w") as f:
    f.write(f"✅ Hello from GitHub Actions!\n")
    f.write(f"🕒 Current UTC time: {now}\n")

print("Output written to output.txt")

  
