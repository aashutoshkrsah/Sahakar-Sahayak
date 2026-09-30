"""GOLD: the AI cutter's plans (backend/data/medallion/cuts/*.json) applied to the silver text,
turned into labelled pieces, and CHECKED before anything is saved.

Every piece gets a "Platinum" label (its full address), e.g.
  Karnataka Co-operative Societies Act, 1959 › Chapter IV – ... › Section 28 – Special general meeting › Page 64
The PDF's own words are never changed: a piece's text is exactly the silver lines between two cut points.

Safety checks (the build stops if any fails):
  1. nothing lost      -- every silver line is in exactly one piece
  2. nothing invented  -- every piece's text is found word for word in the silver text
  3. every piece has a label, and no piece is empty
Plus a quality report: sizes, and how many answer-key quotes of the benchmarks sit inside ONE piece
(old 800-letter pieces vs new gold pieces).
Run:  python3 -m backend.pipeline.gold"""
import os
import re
import glob
import json
from collections import defaultdict

from backend.pipeline.common import (SILVER_PATH, CUTS_DIR, GOLD_PATH, REPORT_PATH, BASE_DIR,
                                     official_name, doc_key, load, save)

MAX_CHARS = 1800        # a section longer than this is split into parts (at sentence ends)
PART_TARGET = 1300      # size of each part when splitting
PART_OVERLAP = 150      # letters repeated between parts of the same section, so no rule is cut in half
TINY = 100              # a piece shorter than this (e.g. a heading alone) is joined to the next piece


def _norm(t):
    return re.sub(r"[^0-9a-z]+", "", (t or "").lower())


def _split_long(body):
    """Split a long section at sentence ends into ~PART_TARGET-letter parts with a small overlap."""
    if len(body) <= MAX_CHARS:
        return [body]
    parts, start = [], 0
    while start < len(body):
        end = min(start + PART_TARGET, len(body))
        if end < len(body):
            cut = max(body.rfind(". ", start + PART_TARGET // 2, end), body.rfind("; ", start + PART_TARGET // 2, end),
                      body.rfind(": ", start + PART_TARGET // 2, end))
            if cut != -1:
                end = cut + 1
            if len(body) - end < 300:       # don't leave a tiny last part
                end = len(body)
        parts.append(body[start:end].strip())
        if end >= len(body):
            break
        start = max(end - PART_OVERLAP, start + 1)
        sp = body.find(" ", start)          # start the overlap at a word boundary
        start = sp + 1 if 0 <= sp < end else start
    return parts


def _pages_txt(pages):
    return f"Page {pages[0]}" if len(pages) == 1 else f"Pages {pages[0]}-{pages[-1]}"


def build():
    silver = load(SILVER_PATH)
    lines_by_doc = defaultdict(list)                     # doc -> [(line_id, page, text)] in order
    for p in sorted(silver, key=lambda x: (x["document"], x["page"])):
        for l in p["lines"]:
            lines_by_doc[p["document"]].append((l["id"], p["page"], l["text"]))

    plans = {}
    for f in glob.glob(os.path.join(CUTS_DIR, "*.json")):
        plan = load(f)
        plans[plan["doc_key"].lower()] = plan["cuts"]

    gold, problems = [], []
    covered = defaultdict(list)                          # doc -> every line id placed in a section
    for doc, lines in lines_by_doc.items():
        cuts = plans.get(doc_key(doc).lower())
        if not cuts:
            problems.append(f"{doc}: no cut plan")
            continue
        pos = {lid: i for i, (lid, _, _) in enumerate(lines)}
        bad = [c["at"] for c in cuts if c["at"] not in pos]
        if bad:
            problems.append(f"{doc}: unknown cut ids {bad[:5]}")
            continue
        starts = sorted({pos[c["at"]]: c["label"].strip() for c in cuts}.items())
        if starts[0][0] != 0:
            problems.append(f"{doc}: first cut is not at the first line")
            continue
        sections = []
        for n, (s, label) in enumerate(starts):
            e = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
            chunk = lines[s:e]
            sections.append({"label": label, "lines": [x[0] for x in chunk],
                             "pages": sorted({x[1] for x in chunk}),
                             "body": " ".join(" ".join(x[2] for x in chunk).split())})
        # join tiny pieces (a heading alone) to the next one; the next piece keeps its own label
        merged = []
        carry = None
        for sec in sections:
            if carry:
                sec = {"label": sec["label"], "lines": carry["lines"] + sec["lines"],
                       "pages": sorted(set(carry["pages"]) | set(sec["pages"])),
                       "body": (carry["body"] + " " + sec["body"]).strip()}
                carry = None
            if len(sec["body"]) < TINY and sec is not sections[-1]:
                carry = sec
                continue
            merged.append(sec)
        if carry:
            merged.append(carry)
        name = official_name(doc)
        for sec in merged:
            covered[doc] += sec["lines"]
            parts = _split_long(sec["body"])
            for k, body in enumerate(parts, start=1):
                label = f"{name} › {sec['label']} › {_pages_txt(sec['pages'])}"
                if len(parts) > 1:
                    label += f" › Part {k} of {len(parts)}"
                gold.append({"document": doc, "page": sec["pages"][0], "pages": sec["pages"],
                             "label": label, "body": body, "text": f"[{label}]\n{body}"})

    # ---- safety checks ----
    for doc, lines in lines_by_doc.items():
        ids = [x[0] for x in lines]
        used = covered[doc]
        if sorted(used) != sorted(ids):
            lost = sorted(set(ids) - set(used))
            twice = len(used) - len(set(used))
            problems.append(f"{doc}: {len(lost)} lines not in any piece {lost[:3]}, {twice} lines in two pieces")
        whole_text = _norm(" ".join(x[2] for x in lines))
        for g in (g for g in gold if g["document"] == doc):
            if not g["body"].strip() or not g["label"].strip():
                problems.append(f"{doc} p{g['page']}: empty piece or label")
            elif _norm(g["body"]) not in whole_text:
                problems.append(f"{doc} p{g['page']}: piece text not found in the PDF text (invented?)")
    if problems:
        raise SystemExit("GOLD NOT SAVED -- checks failed:\n  " + "\n  ".join(problems[:40]))

    save(GOLD_PATH, {"version": 1, "pieces": gold})
    _report(gold, lines_by_doc)
    print(f"gold: {len(gold)} labelled pieces from {len(lines_by_doc)} PDFs -> {GOLD_PATH} (all checks passed)")
    return gold


def _report(gold, lines_by_doc):
    """Quality report: sizes + answer-key quotes that sit inside ONE piece (old pieces vs gold pieces)."""
    sizes = sorted(len(g["body"]) for g in gold)
    old_path = os.path.join(BASE_DIR, "backend", "data", "chunks_cache.json")
    old = load(old_path)["chunks"] if os.path.exists(old_path) else []
    banks = [f for f in ("benchmark_questions_all.json", "benchmark_questions_200.json", "benchmark_questions_100.json")
             if os.path.exists(os.path.join(BASE_DIR, f))]
    quotes = []
    for f in banks:
        for q in load(os.path.join(BASE_DIR, f))["questions"]:
            if q.get("evidence") and q.get("doc"):
                quotes.append((q["doc"].lower(), _norm(q["evidence"])))

    def inside(pieces, key):
        return sum(1 for d, ev in quotes if any(d in p["document"].lower() and ev in _norm(p[key]) for p in pieces))
    old_in, new_in = inside(old, "text"), inside(gold, "body")
    lines = [
        "# Gold pieces: quality report", "",
        f"- Pieces: **{len(gold)}** from {len(lines_by_doc)} PDFs (old system: {len(old)} pieces of 800 letters)",
        f"- Size (letters): min {sizes[0]} · median {sizes[len(sizes) // 2]} · max {sizes[-1]}",
        f"- Every piece has a full label, e.g. `{gold[len(gold) // 3]['label']}`",
        f"- Answer-key quotes (all benchmark questions, {len(quotes)} quotes) found whole inside ONE piece: "
        f"old pieces **{old_in}/{len(quotes)}** ({100 * old_in / max(1, len(quotes)):.1f}%) → "
        f"gold pieces **{new_in}/{len(quotes)}** ({100 * new_in / max(1, len(quotes)):.1f}%)",
        "- Checks passed: nothing lost, nothing invented, no empty piece, every piece labelled.", "",
        "## Pieces per PDF", "", "| PDF | Pieces |", "|---|---|",
    ] + [f"| {official_name(d)} | {sum(1 for g in gold if g['document'] == d)} |" for d in sorted(lines_by_doc)]
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[2:7]))


if __name__ == "__main__":
    build()
