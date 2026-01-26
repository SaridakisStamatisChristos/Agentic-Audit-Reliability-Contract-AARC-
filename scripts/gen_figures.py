#!/usr/bin/env python3
from pathlib import Path


FIGURES = {
    "arf_architecture.pdf": "ARF Architecture",
    "arf_lifecycle.pdf": "ARF Lifecycle",
}


def make_pdf(path: Path, title: str) -> None:
    contents = f"BT /F1 24 Tf 72 720 Td ({title}) Tj ET"
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(contents)} >>\nstream\n{contents}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    offsets: list[int] = []
    pdf_parts = ["%PDF-1.4\n"]
    for index, obj in enumerate(objects, start=1):
        offsets.append(sum(len(chunk) for chunk in pdf_parts))
        pdf_parts.append(f"{index} 0 obj\n{obj}\nendobj\n")

    xref_offset = sum(len(chunk) for chunk in pdf_parts)
    pdf_parts.append("xref\n")
    pdf_parts.append(f"0 {len(objects) + 1}\n")
    pdf_parts.append("0000000000 65535 f \n")
    for offset in offsets:
        pdf_parts.append(f"{offset:010d} 00000 n \n")
    pdf_parts.append("trailer\n")
    pdf_parts.append(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n")
    pdf_parts.append("startxref\n")
    pdf_parts.append(f"{xref_offset}\n")
    pdf_parts.append("%%EOF\n")

    path.write_bytes("".join(pdf_parts).encode("ascii"))


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    figures_dir = repo_root / "paper" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    for filename, title in FIGURES.items():
        make_pdf(figures_dir / filename, title)


if __name__ == "__main__":
    main()
