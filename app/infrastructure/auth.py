"""TODO"""
import os
from pathlib import Path
import csv
from typing import Dict, List

from dotenv import load_dotenv

load_dotenv()

CSV_PATH = os.getenv("CSV_PATH")

def read_csv(file_path: str):
    """TODO"""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("CSV file not found.")

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

class ClientRepository:
    """TODO"""
    def __init__(self, csv_path: Path = CSV_PATH):
        self.csv_path = csv_path

    def get_all_clients(self) -> List[Dict]:
        """TODO"""
        return read_csv(self.csv_path)