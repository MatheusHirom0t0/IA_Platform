"""TODO"""
from pathlib import Path
from typing import Optional
import csv
import os
from dotenv import load_dotenv

load_dotenv()


def read_csv(file_path: Optional[str] = None):
    if file_path is None:
        file_path = os.getenv("CSV_PATH")

    if not file_path:
        raise RuntimeError("CSV_PATH not found in environment variables.")

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def clean_cpf(cpf: str) -> str:
    return "".join(ch for ch in cpf if ch.isdigit())


def validate_date(date_str: str) -> str:
    parts = date_str.split("-")
    if len(parts) != 3:
        raise TypeError("Invalid date format. Expected YYYY-MM-DD.")

    year, month, day = parts

    if not (year.isdigit() and month.isdigit() and day.isdigit()):
        raise TypeError("Invalid date format. Only digits allowed.")

    year_i = int(year)
    month_i = int(month)
    day_i = int(day)

    if not (1 <= month_i <= 12):
        raise TypeError("Invalid month.")

    if not (1 <= day_i <= 31):
        raise TypeError("Invalid day.")

    return date_str


def normalize_birth_date(raw_birth_date: str) -> str:
    """
    Normaliza para YYYY-MM-DD aceitando:
    - YYYY-MM-DD  (2000-11-30)
    - DD-MM-YYYY  (30-11-2000)
    - YYYYMMDD    (20001130)
    - DDMMYYYY    (30112000)
    """
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
            year = raw[0:4]
            month = raw[4:6]
            day = raw[6:8]

        normalized = f"{year}-{month}-{day}"
        return validate_date(normalized)

    raise TypeError(
        "Invalid date format. Use YYYY-MM-DD, DD-MM-YYYY, YYYYMMDD or DDMMYYYY."
    )
