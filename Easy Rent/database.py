import json
import os
from config import DATA_FILE

def verileri_yukle():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def verileri_kaydet(veriler):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=4)

GECMIS_DOSYA = "kiralama_gecmisi.json"

def gecmis_kaydet(kayit):
    veriler = []
    if os.path.exists(GECMIS_DOSYA):
        with open(GECMIS_DOSYA, "r", encoding="utf-8") as f:
            veriler = json.load(f)
    veriler.append(kayit)
    with open(GECMIS_DOSYA, "w", encoding="utf-8") as f:
        json.dump(veriler, f, indent=4, ensure_ascii=False)
