from pathlib import Path
import json
import re

import pymupdf


PDF_PATH = Path("data/policy/USGIC-CSCIndividualHealthInsurance_2017-2018.pdf")
OUTPUT_PATH = Path("artifacts/policy_chunks.jsonl")


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_section(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        if len(line) <= 150 and (
            line.isupper()
            or re.match(r"^(section|chapter|part|\d+[\.\)])", line, re.I)
        ):
            return line

    return "Unknown Section"


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    document = pymupdf.open(PDF_PATH)
    chunk_count = 0

    with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
        for page_number, page in enumerate(document, start=1):
            raw_text = page.get_text("text")
            section = detect_section(raw_text)
            text = clean_text(raw_text)

            if not text:
                continue

            words = text.split()
            chunk_size = 180

            for start in range(0, len(words), chunk_size):
                chunk_words = words[start:start + chunk_size]
                chunk_text = " ".join(chunk_words)

                chunk = {
                    "chunk_id": f"page_{page_number}_chunk_{chunk_count + 1}",
                    "page": page_number,
                    "section": section,
                    "text": chunk_text,
                }

                output_file.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                chunk_count += 1

    print(f"Created {chunk_count} policy chunks.")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()