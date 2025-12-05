"""Utilities and repository for reading client data from CSV files."""
from typing import Optional, Dict, List
import os
from pathlib import Path
import csv
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = os.getenv("CSV_PATH")

def read_csv(file_path: Optional[str] = None):
    """Reads a CSV file and returns a list of rows as dictionaries."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("CSV file not found.")

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

class ClientRepository:
    """Repository for accessing client data stored in a CSV file."""
    def __init__(self, csv_path: Path = CSV_PATH):
        self.csv_path = csv_path

    def get_all_clients(self) -> List[Dict]:
        """Returns all clients loaded from the CSV file."""
        return read_csv(self.csv_path)
