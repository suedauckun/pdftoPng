from fastapi import FastAPI, UploadFile, File, HTTPException
from pdf2image import convert_from_bytes
from io import BytesIO
import base64
import io
import pikepdf  

app = FastAPI()

# --- YARDIMCI FONKSİYON ---
def pikepdf_to_base64(pikepdf_obj):
    """Pikepdf nesnesini base64 string'e çevirir."""
    out_stream = io.BytesIO()
    pikepdf_obj.save(out_stream)
    return base64.b64encode(out_stream.getvalue()).decode('utf-8')

@app.post("/convert")
async def pdf_to_png(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    try:
        pages = convert_from_bytes(pdf_bytes, dpi=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görüntü oluşturma hatası: {str(e)}")

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

@app.post("/explode-pdf")
async def explode_pdf(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        pdf_stream = io.BytesIO(file_content)
        
        pdf = pikepdf.open(pdf_stream)
        output_files = []
        total_pages = len(pdf.pages)
        
        for i, page in enumerate(pdf.pages):
            new_pdf = pikepdf.new()
            new_pdf.pages.append(page)
            
            output_files.append({
                "filename": f"page_{i+1}.pdf",
                "data_b64": pikepdf_to_base64(new_pdf),
                "type": "single_page"
            })
            
        return {
            "total_pages": total_pages,
            "files": output_files
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF işleme hatası: {str(e)}")

@app.post("/chunk-pdf")
async def chunk_pdf(file: UploadFile = File(...), size: int = 15):
    try:
        file_content = await file.read()
        pdf_stream = io.BytesIO(file_content)
        
        pdf = pikepdf.open(pdf_stream)
        total_pages = len(pdf.pages)
        output_files = []
        
        # 4. Belirlenen aralıklarla döngü kur
        for i in range(0, total_pages, size):
            new_pdf = pikepdf.new()
            
            # Sayfa dilimini al (örn: 0-15, 15-30...)
            pages_slice = pdf.pages[i : i + size]
            new_pdf.pages.extend(pages_slice)
            
            part_number = (i // size) + 1
            
            output_files.append({
                "filename": f"part_{part_number}.pdf",
                "data_b64": pikepdf_to_base64(new_pdf),
                "page_count": len(pages_slice),
                "type": "chunked_part"
            })
            
        return output_files

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunk hatası: {str(e)}")