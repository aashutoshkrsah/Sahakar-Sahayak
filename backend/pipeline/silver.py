"""SILVER: cleaned text, line by line, every line with a stable id "P<page>.L<n>".
Cleaning (nothing is rewritten, only tidied):
  - broken words joined back: "co -operative" -> "co-operative", "sub -section" -> "sub-section"
  - repeated page headers / footers removed (a line pattern found at the top or bottom of at
    least a quarter of a PDF's pages, e.g. "www.pmfby.gov.in", "File No: .../Credit-II(pt)")
  - lone page numbers removed
  - extra spaces squeezed
  - very long lines (pages that came out of the PDF as one line) split at sentence ends
Run:  python3 -m backend.pipeline.silver"""
import re
from collections import Counter, defaultdict
from backend.pipeline.common import BRONZE_PATH, SILVER_PATH, load, save

EDGE = 3                      # lines checked at the top and bottom of each page
BROKEN_WORD = re.compile(r"\b([A-Za-z]{2,})\s+-([A-Za-z]{2,})\b")
PAGE_NUMBER = re.compile(r"^\s*(page\s*)?[\divxlcIVXLC]{1,5}\s*(of\s*\d+)?\s*$", re.I)


def _shape(line):
    return re.sub(r"\d+", "#", line.strip())


LONG_LINE = 300               # longer lines (PDFs without line breaks) are split at sentence ends
SENTENCE_END = re.compile(r"(?<=[.;:])\s+(?=(?:\(?[A-Za-z0-9]{1,4}[).]\s)|[A-Z(\d])")


def split_long(line):
    """A PDF page that came out as one giant line is split at sentence / clause starts so it can be cut."""
    if len(line) <= LONG_LINE:
        return [line]
    parts, buf = [], ""
    for piece in SENTENCE_END.split(line):
        if buf and len(buf) + len(piece) > LONG_LINE:
            parts.append(buf)
            buf = piece
        else:
            buf = f"{buf} {piece}".strip()
    if buf:
        parts.append(buf)
    return parts


def clean_line(line):
    line = BROKEN_WORD.sub(r"\1-\2", line)
    line = BROKEN_WORD.sub(r"\1-\2", line)        # twice, for "co -operative -societies"
    return re.sub(r"[ \t]+", " ", line).strip()


def build():
    bronze = load(BRONZE_PATH)
    by_doc = defaultdict(list)
    for p in bronze:
        by_doc[p["document"]].append(p)

    silver, removed = [], Counter()
    for doc, pages in by_doc.items():
        edge_shapes = Counter()
        for p in pages:
            lines = [l for l in p["text"].split("\n") if l.strip()]
            for l in set(lines[:EDGE] + lines[-EDGE:]):
                edge_shapes[_shape(l)] += 1
        repeated = {s for s, n in edge_shapes.items() if n >= max(3, len(pages) * 0.25) and len(s) > 1 and s != "#"}
        for p in pages:
            raw = [l for l in p["text"].split("\n") if l.strip()]
            out, n = [], 0
            for idx, l in enumerate(raw):
                at_edge = idx < EDGE or idx >= len(raw) - EDGE
                if at_edge and (PAGE_NUMBER.match(l) or _shape(l) in repeated):
                    removed[doc] += 1
                    continue
                for c in split_long(clean_line(l)):
                    if c:
                        n += 1
                        out.append({"id": f"P{p['page']}.L{n}", "text": c})
            silver.append({"document": doc, "page": p["page"], "lines": out})
    save(SILVER_PATH, silver)
    total = sum(len(p["lines"]) for p in silver)
    print(f"silver: {total} clean lines on {len(silver)} pages; removed headers/footers/page numbers: "
          + ", ".join(f"{d[:18]} {n}" for d, n in removed.items()))
    return silver


if __name__ == "__main__":
    build()
