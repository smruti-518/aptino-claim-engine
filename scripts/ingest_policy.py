from pathlib import Path
import fitz  # PyMuPDF

PDF_PATH = Path("data/policy/USGIC-CSCIndividualHealthInsurance_2017-2018.pdf")
OUTPUT_PATH = Path("artifacts/policy_text.txt")


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    document = fitz.open(PDF_PATH)
    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text")
        pages.append(f"\n--- PAGE {page_number} ---\n{text}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(pages), encoding="utf-8")

    print(f"Extracted {len(document)} pages.")
    print(f"Saved text to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()