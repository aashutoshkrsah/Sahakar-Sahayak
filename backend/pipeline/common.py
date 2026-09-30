"""Shared paths and names for the Medallion pipeline."""
import os, json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS_DIR = os.path.join(BASE_DIR, "backend", "data", "documents")
MED_DIR = os.path.join(BASE_DIR, "backend", "data", "medallion")
BRONZE_PATH = os.path.join(MED_DIR, "bronze.json")
SILVER_PATH = os.path.join(MED_DIR, "silver.json")
CUTS_DIR = os.path.join(MED_DIR, "cuts")            # the AI cutter's plans, one file per PDF
GOLD_PATH = os.path.join(MED_DIR, "gold.json")
GOLD_EMB_PATH = os.path.join(MED_DIR, "gold_embeddings.npy")
GOLD_EMB_META = os.path.join(MED_DIR, "gold_embeddings_meta.json")
REPORT_PATH = os.path.join(MED_DIR, "quality_report.md")

# Short key (used everywhere in the project) -> official name shown in every label
OFFICIAL_NAMES = {
    "11of1959": "Karnataka Co-operative Societies Act, 1959",
    "247816": "Multi-State Co-operative Societies (Amendment) Act, 2023",
    "405MDD58": "RBI Kisan Credit Card Directions, 2026 (Rural Co-operative Banks)",
    "FINAL_UPISOGs": "Unified Package Insurance Scheme (UPIS) Operational Guidelines",
    "Initiatives": "Ministry of Cooperation: Initiatives Booklet (Nov 2025)",
    "Model Byelaws": "Model Bye-laws for PACS (Primary Agricultural Credit Societies)",
    "New Schemes": "Farmer Schemes Booklet (PMFBY, KCC and others)",
    "PMKSY": "PMKSY (Pradhan Mantri Krishi Sinchayee Yojana) Operational Reference 2021-26",
    "RWBCIS": "Restructured Weather Based Crop Insurance Scheme (RWBCIS) Guidelines",
    "PM-KISAN": "PM-KISAN Operational Guidelines (Revised)",
    "doc1": "PMFBY (Pradhan Mantri Fasal Bima Yojana) Operational Guidelines 2023",
}


def official_name(pdf_name):
    for key, name in OFFICIAL_NAMES.items():
        if key.lower() in pdf_name.lower():
            return name
    return os.path.splitext(pdf_name)[0]


def doc_key(pdf_name):
    for key in OFFICIAL_NAMES:
        if key.lower() in pdf_name.lower():
            return key
    return os.path.splitext(pdf_name)[0]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=0)
    os.replace(tmp, path)
