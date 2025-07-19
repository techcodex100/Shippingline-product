import time
import requests
import psutil
import os
import pandas as pd

CSV_FILE = "shipping_docs_sample.csv"
SAVE_FOLDER = "generated_pdfs"
ENDPOINT = "https://shippingline-product.onrender.com/generate-pdf/"

os.makedirs(SAVE_FOLDER, exist_ok=True)

def send_requests():
    print("🚀 Auto PDF Generation & Download Started...")
    start = time.time()

    df = pd.read_csv(CSV_FILE)

    for i, row in df.iterrows():
        print(f"\n📤 Generating PDF #{i+1}...")

        try:
            response = requests.post(
                ENDPOINT,
                json=row.to_dict(),
                allow_redirects=True
            )

            if response.status_code == 200 and response.headers.get("content-type") == "application/pdf":
                file_path = os.path.join(SAVE_FOLDER, f"shipping_doc_{i+1}.pdf")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ PDF #{i+1} saved at: {file_path}")
            else:
                print(f"❌ Failed Request #{i+1} - Status: {response.status_code}")
                print(f"📝 Response: {response.text}")

        except Exception as e:
            print(f"💥 Error on PDF #{i+1}: {e}")

    end = time.time()
    print("\n📊 Performance Report:")
    print(f"⏱️ Time Taken: {round(end - start, 2)} sec")
    print(f"🧠 Memory Used: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
    print(f"⚙️ CPU Usage: {psutil.cpu_percent(interval=1)}%")

if __name__ == "__main__":
    send_requests()
