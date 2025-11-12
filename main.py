"""Main FastAPI application for the PDF Library."""

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import os
import aiofiles
from datetime import datetime
import PyPDF2
import shutil
import logging
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Open PDF Library")

# Get the absolute path of the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Create necessary directories
os.makedirs(os.path.join(BASE_DIR, "pdfs"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)

logger.info("Application initialized with directories: pdfs, static, templates")

class PDFLibrary:
    def __init__(self):
        self.pdf_dir = os.path.join(BASE_DIR, "pdfs")
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        logger.info(f"PDFLibrary initialized with directory: {self.pdf_dir}")

    async def save_pdf(self, file: UploadFile) -> str:
        """Save uploaded PDF file and return filename."""
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Create a temporary file for validation
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            content = await file.read()
            temp_file.write(content)
            temp_file.seek(0)

            # Check file size
            file_size = len(content)
            if file_size > self.max_file_size:
                raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")

            # Validate PDF
            try:
                PyPDF2.PdfReader(temp_file)
            except Exception as e:
                raise HTTPException(status_code=400, detail="Invalid file")

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(self.pdf_dir, filename)

            # Save file
            temp_file.seek(0)
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            return filename
        finally:
            temp_file.close()
            os.unlink(temp_file.name)

        logger.info(f"File saved: {filename}")
        return filename

    def get_all_pdfs(self) -> List[dict]:
        """Get list of all PDF files with metadata."""
        pdfs = []
        for filename in os.listdir(self.pdf_dir):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(self.pdf_dir, filename)
                stats = os.stat(file_path)
                
                # Get PDF metadata
                try:
                    with open(file_path, 'rb') as f:
                        pdf = PyPDF2.PdfReader(f)
                        num_pages = len(pdf.pages)
                except Exception:
                    num_pages = 0

                pdfs.append({
                    'filename': filename,
                    'size': stats.st_size,
                    'uploaded_at': datetime.fromtimestamp(stats.st_mtime),
                    'pages': num_pages
                })
        
        return sorted(pdfs, key=lambda x: x['uploaded_at'], reverse=True)

    def get_pdf_path(self, filename: str) -> str:
        """Get full path of PDF file."""
        file_path = os.path.join(self.pdf_dir, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        return file_path

# Initialize PDF library
pdf_library = PDFLibrary()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page with list of PDFs."""
    pdfs = pdf_library.get_all_pdfs()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "pdfs": pdfs}
    )

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file."""
    try:
        filename = await pdf_library.save_pdf(file)
        return {"filename": filename, "status": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error uploading file")

@app.get("/pdf/{filename}")
async def get_pdf(filename: str):
    """View a PDF file in browser."""
    file_path = pdf_library.get_pdf_path(filename)
    return FileResponse(
        file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"}
    )

@app.get("/search")
async def search_pdfs(
    query: str = Query(..., min_length=1),
    request: Request = None
):
    """Search PDFs by filename."""
    all_pdfs = pdf_library.get_all_pdfs()
    results = [
        pdf for pdf in all_pdfs
        if query.lower() in pdf['filename'].lower()
    ]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "pdfs": results,
            "search_query": query
        }
    )

@app.delete("/pdf/{filename}")
async def delete_pdf(filename: str):
    """Delete a PDF file."""
    try:
        file_path = pdf_library.get_pdf_path(filename)
        os.remove(file_path)
        return {"status": "success", "message": f"Deleted {filename}"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting file")