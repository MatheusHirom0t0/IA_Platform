"""TODO"""
import csv
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def extract_digits(text: str) -> str:
    """TODO"""
    return "".join(ch for ch in text if ch.isdigit())


def clean_cpf(cpf: str) -> str:
    """TODO"""
    return extract_digits(cpf)

def extract_cpf_digits(raw_cpf: str) -> str:
    """TODO"""
    return "".join(ch for ch in raw_cpf if ch.isdigit())

def normalize_birth_date(raw_birth_date: str) -> str:
    """TODO"""
    raw = raw_birth_date.strip()

    formatos = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y%m%d",
        "%d%m%Y",
    ]

    for fmt in formatos:
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise TypeError("Formato de data inválido.")



def read_csv(path: Optional[str] = None):
    """TODO"""
    path = path or os.getenv("CSV_PATH")
    if not path:
        raise RuntimeError("CSV_PATH not set.")

    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    with file.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate_date(date_str: str) -> str:
    """TODO"""
    parts = date_str.split("-")
    if len(parts) != 3:
        raise TypeError("Invalid date format. Expected YYYY-MM-DD.")

    year, month, day = parts

    if any(not p.isdigit() for p in (year, month, day)):
        raise TypeError("Invalid date format. Only digits allowed.")

    year_i = int(year)
    month_i = int(month)
    day_i = int(day)

    if not 1900 <= year_i <= 2100:
        raise TypeError("Invalid year.")

    if not 1 <= month_i <= 12:
        raise TypeError("Invalid month.")

    if not 1 <= day_i <= 31:
        raise TypeError("Invalid day.")

    return date_str

def normalize_date(raw_birth_date: str) -> str:
    """TODO"""
    raw = raw_birth_date.strip()

    if "-" in raw:
        parts = raw.split("-")
        if len(parts) != 3:
            raise TypeError(
                "Invalid date format. Use YYYY-MM-DD, DD-MM-YYYY, YYYYMMDD or DDMMYYYY."
            )

        if len(parts[0]) == 4:
            year, month, day = parts
        elif len(parts[2]) == 4:
            day, month, year = parts
        else:
            raise TypeError(
                "Invalid date format. Use YYYY-MM-DD, DD-MM-YYYY, YYYYMMDD or DDMMYYYY."
            )

        normalized = f"{year}-{month}-{day}"
        return validate_date(normalized)

    if len(raw) == 8 and raw.isdigit():
        first4 = int(raw[0:4])
        last4 = int(raw[4:8])

        if 1900 <= first4 <= 2100:
            year = raw[0:4]
            month = raw[4:6]
            day = raw[6:8]
        elif 1900 <= last4 <= 2100:
            day = raw[0:2]
            month = raw[2:4]
            year = raw[4:8]
        else:
            raise TypeError(
                "Invalid date format. Use YYYY-MM-DD, DD-MM-YYYY, YYYYMMDD or DDMMYYYY."
            )

        normalized = f"{year}-{month}-{day}"
        return validate_date(normalized)

    raise TypeError(
        "Invalid date format. Use YYYY-MM-DD, DD-MM-YYYY, YYYYMMDD or DDMMYYYY."
    )
