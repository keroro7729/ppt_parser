from pathlib import Path
import json
import pandas as pd
from ppt_parser.ollama_client import OllamaClient
from ppt_parser.logger import setup_logger
import logging
import subprocess


BASE_DIR = Path(__file__).resolve().parents[2] / "sample"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"

logger = setup_logger(level=logging.INFO)

def parse_ppt(file_name: str) :
    pptx_path = BASE_DIR / file_name
    pdf_path = convert_pptx_to_pdf(pptx_path)
    logger.info(f"PDF 변환 완료: {pdf_path}")

    client = OllamaClient(
        base_url="http://127.0.0.1:11434",
        model="ibm/granite-docling",
        timeout=10 * 60,
    )

    response = client.generate_with_file(pdf_path)
    output_path = OUTPUT_DIR / f"{pptx_path.stem}_docling.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response)
    logger.info(f"결과 저장 완료: {output_path}")

    return response

def convert_pptx_to_pdf(pptx_path: Path) -> Path:
    pdf_path = pptx_path.with_suffix(".pdf")

    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        str(pptx_path),
        "--outdir",
        str(pptx_path.parent),
    ]

    subprocess.run(cmd, check=True)
    return pdf_path

if __name__ == "__main__":
    sample_file = "To_Be_MM_1.1.1.pptx"
    logger.info("start parsing " + sample_file)
    result = parse_ppt(sample_file)