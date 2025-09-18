import datetime

def main():
    now = datetime.datetime.utcnow()
    with open("output.txt", "w") as f:
        f.write("✅ Hello from GitHub Actions!\n")
        f.write(f"🕒 Current UTC time: {now}\n")
    print("Output written to output.txt")

if __name__ == "__main__":
    main()
