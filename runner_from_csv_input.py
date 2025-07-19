import time
import requests
import psutil
import os

SAVE_FOLDER = "generated_pdfs"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def generate_unique_input(index):
    return {
        "shipper_page1": f"Shipper Company {index}",
        "consignee_page1": f"Consignee {index}",
        "bl_date_page1": f"2025-07-{(index % 30) + 1:02d}",
        "goods_page1": f"Test Goods Description {index}",
        "invoice_page1": f"INV{1000 + index}",
        "vessel_page1": f"Vessel-{index}",
        "lc_no_page1": f"LCNO-{index}",
        "dated_page1": f"2025-07-{(index % 30) + 1:02d}",
        "with_by_page1": f"With Person {index}",
        "for_by_page1": f"For Person {index}",
        "signature_page1": f"Signature {index}",

        "shipper_page2": f"Shipper Company {index}",
        "consignee_page2": f"Consignee {index}",
        "bl_date_page2": f"2025-07-{(index % 30) + 1:02d}",
        "goods_page2": f"Test Goods Description {index}",
        "invoice_page2": f"INV{1000 + index}",
        "vessel_page2": f"Vessel-{index}",
        "lc_no_page2": f"LCNO-{index}",
        "dated_page2": f"2025-07-{(index % 30) + 1:02d}",
        "signature_page2": f"Signature {index}",

        "lc_opener_page3": f"LC Opener {index}",
        "beneficiary_page3": f"Beneficiary {index}",
        "amount_page3": f"{1000 + index * 10} USD",
        "lc_no_page3": f"LCNO-{index}",
        "dated_page3": f"2025-07-{(index % 30) + 1:02d}",
        "swift_code_page3": f"SWIFT{index:04d}",
        "bank_name_page3": f"Bank {index}",
        "for_by_page3": f"For Person {index}",
        "signature_page3": f"Signature {index}"
    }

def send_requests():
    print("🚀 Auto PDF Generation & Download Started...")
    start = time.time()

    total_pdfs = 50  # Change as needed

    for i in range(total_pdfs):
        print(f"\n📤 Generating PDF #{i+1}...")

        data = generate_unique_input(i + 1)
        try:
            response = requests.post(
                "https://shippingline-product.onrender.com/generate-pdf/",
                json=data,
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
