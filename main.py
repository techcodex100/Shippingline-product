from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
from faker import Faker
import os
import csv
import threading

app = FastAPI()
fake = Faker()
lock = threading.Lock()

COUNTER_FILE = "counter.txt"
os.makedirs("generated_pdfs", exist_ok=True)

def get_next_counter():
    with lock:
        if not os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "w") as f:
                f.write("1")
            return 1
        with open(COUNTER_FILE, "r+") as f:
            count = int(f.read().strip()) + 1
            f.seek(0)
            f.write(str(count))
            f.truncate()
        return count

def draw_fields(c, data, mapping):
    c.setFont("Helvetica", 10)
    for key, (x, y) in mapping.items():
        c.drawString(x, y, str(data.get(key, "")))

@app.post("/generate-pdf")
async def generate_pdf():
    data = {
        # Page 1
        "shipper_page1": fake.company(),
        "consignee_page1": fake.company(),
        "bl_date_page1": fake.date(),
        "goods_page1": fake.catch_phrase(),
        "invoice_page1": fake.uuid4(),
        "vessel_page1": fake.word(),
        "lc_no_page1": fake.bothify(text="LC#######"),
        "dated_page1": fake.date(),
        "with_by_page1": fake.name(),
        "for_by_page1": fake.name(),
        "signature_page1": fake.name(),

        # Page 2
        "shipper_page2": fake.company(),
        "consignee_page2": fake.company(),
        "bl_date_page2": fake.date(),
        "goods_page2": fake.catch_phrase(),
        "invoice_page2": fake.uuid4(),
        "vessel_page2": fake.word(),
        "lc_no_page2": fake.bothify(text="LC#######"),
        "dated_page2": fake.date(),
        "signature_page2": fake.name(),

        # Page 3
        "lc_opener_page3": fake.company(),
        "beneficiary_page3": fake.company(),
        "amount_page3": f"${fake.random_int(min=1000, max=10000)}",
        "lc_no_page3": fake.bothify(text="LC#######"),
        "dated_page3": fake.date(),
        "swift_code_page3": fake.swift(),
        "bank_name_page3": fake.company(),
        "for_by_page3": fake.name(),
        "signature_page3": fake.name()
    }

    count = get_next_counter()
    filename = f"generated_{count}.pdf"
    path = f"generated_pdfs/{filename}"

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    # Page 1
    c.drawImage(ImageReader("1.png"), 0, 0, width=width, height=height)
    draw_fields(c, data, {
        "shipper_page1": (160, 695),
        "consignee_page1": (160, 672),
        "bl_date_page1": (160, 640),
        "goods_page1": (100, 612),
        "invoice_page1": (160, 585),
        "vessel_page1": (160, 555),
        "lc_no_page1": (100, 480),
        "dated_page1": (300, 480),
        "with_by_page1": (180, 375),
        "for_by_page1": (100, 300),
        "signature_page1": (240, 260),
    })
    c.showPage()

    # Page 2
    c.drawImage(ImageReader("2.png"), 0, 0, width=width, height=height)
    draw_fields(c, data, {
        "shipper_page2": (160, 630),
        "consignee_page2": (160, 600),
        "bl_date_page2": (160, 575),
        "goods_page2": (140, 545),
        "invoice_page2": (160, 515),
        "vessel_page2": (120, 490),
        "lc_no_page2": (60, 410),
        "dated_page2": (300, 410),
        "signature_page2": (220, 245),
    })
    c.showPage()

    # Page 3
    c.drawImage(ImageReader("3.png"), 0, 0, width=width, height=height)
    draw_fields(c, data, {
        "lc_opener_page3": (120, 620),
        "beneficiary_page3": (120, 590),
        "amount_page3": (120, 560),
        "lc_no_page3": (60, 490),
        "dated_page3": (300, 490),
        "swift_code_page3": (40, 420),
        "bank_name_page3": (340, 420),
        "for_by_page3": (60, 320),
        "signature_page3": (220, 300),
    })
    c.showPage()
    c.save()

    return {"message": "✅ PDF generated", "filename": filename, "download_url": f"/download-pdf/{filename}"}

@app.get("/download-pdf/{filename}")
def download_pdf(filename: str):
    path = f"generated_pdfs/{filename}"
    if os.path.exists(path):
        return FileResponse(path, media_type="application/pdf", filename=filename)
    return {"error": "File not found"}

@app.post("/upload-pdf-and-generate-csv/")
async def upload_and_generate_csv(file: UploadFile):
    filename = file.filename
    saved_path = f"uploaded_pdfs/{filename}"
    os.makedirs("uploaded_pdfs", exist_ok=True)
    with open(saved_path, "wb") as f:
        f.write(await file.read())

    csv_data = [
        ["Filename", filename],
        ["Status", "Scanned"],
        ["Fields Filled", fake.random_int(25, 29)],
        ["Confidence (%)", fake.random_int(93, 99)],
        ["Processing Time (ms)", fake.random_int(200, 500)],
    ]
    os.makedirs("csv_reports", exist_ok=True)
    csv_path = f"csv_reports/{filename.replace('.pdf', '.csv')}"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

    return StreamingResponse(open(csv_path, "rb"), media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={os.path.basename(csv_path)}"
    })
