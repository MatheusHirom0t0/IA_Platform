# app/utils/auth_utils.py
from pathlib import Path
import csv
import os
from dotenv import load_dotenv

load_dotenv()


def read_csv(file_path: str | None = None):
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

    if not (1 <= int(month) <= 12):
        raise TypeError("Invalid month.")

    if not (1 <= int(day) <= 31):
        raise TypeError("Invalid day.")

    return date_str


def normalize_birth_date(raw_birth_date: str) -> str:
    raw_birth_date = raw_birth_date.strip()

    if "-" in raw_birth_date:
        return validate_date(raw_birth_date)

    if len(raw_birth_date) == 8 and raw_birth_date.isdigit():
        year = raw_birth_date[0:4]
        month = raw_birth_date[4:6]
        day = raw_birth_date[6:8]
        normalized = f"{year}-{month}-{day}"
        return validate_date(normalized)

    raise TypeError("Invalid date format. Expected YYYY-MM-DD or YYYYMMDD.")
