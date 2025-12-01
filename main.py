from fastapi import FastAPI, UploadFile, File
from pdf2image import convert_from_bytes
from io import BytesIO
import base64

app = FastAPI()

@app.post("/convert")
async def pdf_to_png(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    # Convert PDF → list of images
    pages = convert_from_bytes(pdf_bytes, dpi=200)

    output_images = []

    for page in pages:
        buffer = BytesIO()
        page.save(buffer, format="PNG")
        raw_bytes = buffer.getvalue()

        # Clean Base64 (NO prefix, NO metadata)
        b64 = base64.b64encode(raw_bytes).decode("utf-8")

        output_images.append(b64)

    return {
        "page_count": len(pages),
        "images": output_images
    }
