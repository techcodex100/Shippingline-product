from fastapi import FastAPI, Response
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
import threading
import os

app = FastAPI()
lock = threading.Lock()
COUNTER_FILE = "counter.txt"

class Info(BaseModel):
    # Page 1
    shipper_page1: str
    consignee_page1: str
    bl_date_page1: str
    goods_page1: str
    invoice_page1: str
    vessel_page1: str
    lc_no_page1: str
    dated_page1: str
    with_by_page1: str
    for_by_page1: str
    signature_page1: str

    # Page 2
    shipper_page2: str
    consignee_page2: str
    bl_date_page2: str
    goods_page2: str
    invoice_page2: str
    vessel_page2: str
    lc_no_page2: str
    dated_page2: str
    signature_page2: str

    # Page 3
    lc_opener_page3: str
    beneficiary_page3: str
    amount_page3: str
    lc_no_page3: str
    dated_page3: str
    swift_code_page3: str
    bank_name_page3: str
    for_by_page3: str
    signature_page3: str

def get_next_counter():
    with lock:
        if not os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "w") as f:
                f.write("1")
            return 1
        with open(COUNTER_FILE, "r+") as f:
            count = int(f.read())
            f.seek(0)
            f.write(str(count + 1))
            f.truncate()
            return count

def draw_fields(c, fields, coords):
    c.setFont("Helvetica", 12)
    for key, (x, y) in coords.items():
        value = fields.get(key, "")
        c.drawString(x, y, value)

@app.post("/generate-pdf/")
async def generate_pdf(info: Info):
    pdf_number = get_next_counter()
    filename = f"generated_{pdf_number}.pdf"

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    data = info.dict()

    # -------- Page 1 --------
    c.drawImage(ImageReader("1.png"), 0, 0, width=width, height=height)
    page1_coords = {
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
    }
    draw_fields(c, data, page1_coords)
    c.showPage()

    # -------- Page 2 --------
    c.drawImage(ImageReader("2.png"), 0, 0, width=width, height=height)
    page2_coords = {
        "shipper_page2": (160, 630),
        "consignee_page2": (160, 600),
        "bl_date_page2": (160, 575),
        "goods_page2": (140, 545),
        "invoice_page2": (160, 515),
        "vessel_page2": (120, 490),
        "lc_no_page2": (60, 410),
        "dated_page2": (300, 410),
        "signature_page2": (220, 245),
    }
    draw_fields(c, data, page2_coords)
    c.showPage()

    # -------- Page 3 --------
    c.drawImage(ImageReader("3.png"), 0, 0, width=width, height=height)
    page3_coords = {
        "lc_opener_page3": (120, 620),
        "beneficiary_page3": (120, 590),
        "amount_page3": (120, 560),
        "lc_no_page3": (60, 490),
        "dated_page3": (300, 490),
        "swift_code_page3": (40, 420),
        "bank_name_page3": (340, 420),
        "for_by_page3": (60, 320),
        "signature_page3": (220, 300),
    }
    draw_fields(c, data, page3_coords)
    c.showPage()

    c.save()
    buffer.seek(0)

    return Response(
        content=buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
