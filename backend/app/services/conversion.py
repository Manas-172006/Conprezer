import subprocess
from pathlib import Path

from docx import Document
from fpdf import FPDF


def convert_docx_to_pdf(source: Path, destination: Path) -> None:
    document = Document(source)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    for paragraph in document.paragraphs:
        text = paragraph.text.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 6, text)
    pdf.output(str(destination))


def compress_pdf(source: Path, destination: Path) -> None:
    subprocess.run(
        [
            "gs",
            "-dSAFER",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={destination}",
            str(source),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
