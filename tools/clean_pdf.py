"""Strip PDF catalog actions that ATS portals reject as "active content".

hyperref writes /OpenAction and a /Names tree into every LaTeX PDF. SAP
SuccessFactors refuses such uploads ("The system does not allow files with
active contents"). Rewriting the pages into a fresh document drops both while
keeping text, fonts and layout identical.

Usage: python tools/clean_pdf.py cv/main_<company>_<role>.pdf [more.pdf ...]
"""
import sys

import pypdf


def clean(path: str) -> None:
    reader = pypdf.PdfReader(path)
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    meta = reader.metadata or {}
    writer.add_metadata({k: v for k, v in meta.items() if k in ("/Title", "/Author")})
    with open(path, "wb") as fh:
        writer.write(fh)
    root = pypdf.PdfReader(path).trailer["/Root"]
    bad = [k for k in ("/OpenAction", "/Names", "/AA", "/JavaScript") if k in root]
    print(f"{path}: {'clean' if not bad else 'STILL HAS ' + ', '.join(bad)}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        clean(p)
