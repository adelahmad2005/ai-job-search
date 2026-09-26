# Template: adel-onepage

- **Type:** CV
- **Source extension:** .tex
- **Engine/toolchain:** lualatex
- **Page limit:** 1 page (HARD. Never 2. Longer resumes get filtered out.)
- **Fonts:** Lato Regular/Bold/Italic/BoldItalic (bundled in `fonts/lato/`, and in `cv/fonts/lato/` for compiles in `cv/`)
- **Class/packages:** `adelresume.cls` (article + geometry, fontspec, enumitem, xcolor, hyperref). Must sit next to the `.tex` file (it does in `cv/`).

## Compile command

    cd cv && rm -f <file>.pdf && lualatex -interaction=nonstopmode <file>.tex && python ../tools/clean_pdf.py <file>.pdf

## Style rules

- Replicates Adel's own resumes (`documents/cv/Adel_Abdelmoaty_Resume_AI_Security.pdf`, `..._Services_Presales.pdf`). Those two PDFs are the **reference for format AND language**. Start every tailored resume from `cv/main_example.tex` (AI & Security lane) or `cv/main_base_presales.tex` (Services Presales lane), whichever is closer.
- Section order: Summary, Work Experience, Education, Projects, Skills & Languages. Headings via `\resumesection{}` (uppercase, full-width rule).
- Name `\resumename{ADEL ABDELMOATY}`; two `\contactline{}` lines with email, phone, city, LinkedIn and GitHub written as **plain text** (ATS reads them).
- Entries: `\entry{Title}{Company}{MM/YYYY - MM/YYYY}{City, Country}`. Dates use an ASCII hyphen with spaces, `06/2026 - 08/2026`, never `--`.
- Summary: 3-4 lines, factual, same shape as the originals: degree + graduation date, internship in one sentence, freelance in one clause, "Targeting <role type>."
- Bullets: one per line, start with a past-tense verb, concrete tools and numbers, no adjectives. Dell 6-8 bullets, Bookkeeper 3, Gulf E-Gate 2, education 1, project 1.
- Skills: `\skillline{Label}{items}`; 3-5 lines, most relevant category first.
- Left-aligned (not justified) and no auto-hyphenation, deliberately: both protect the ATS text layer.

## Known pitfalls

- `verify_layout.py` reports "body text inside the bottom margin band, colliding with the footer". That is a phantom: this template has no footer or page number. Ignore that single message; every other layout check still applies.
- Overflow to 2 pages: cut the lowest-relevance bullet or shorten bullets. Never shrink the font below 9.5pt or the margins below 9mm.
- `&` in text must be `\&` (e.g. `Automation \& Data Systems Engineer`, `MITRE ATT\&CK`).
