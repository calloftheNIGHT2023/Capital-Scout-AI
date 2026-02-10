import csv
from typing import List
from .schemas import Lead


REQUIRED_COLUMNS = [
    "first_name",
    "last_name",
    "role",
    "company",
    "industry",
    "stage",
    "email",
]


def read_leads_csv(path: str) -> List[Lead]:
    leads: List[Lead] = []
    seen = set()
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        for row in reader:
            email = (row.get("email") or "").strip().lower()
            if not email or email in seen:
                continue
            seen.add(email)
            lead = Lead(
                first_name=(row.get("first_name") or "").strip(),
                last_name=(row.get("last_name") or "").strip(),
                role=(row.get("role") or "").strip(),
                company=(row.get("company") or "").strip(),
                industry=(row.get("industry") or "").strip(),
                stage=(row.get("stage") or "").strip(),
                email=email,
                source=(row.get("source") or "Apollo").strip() or "Apollo",
            )
            leads.append(lead)
    return leads


def write_clean_csv(path: str, leads: List[Lead]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(REQUIRED_COLUMNS)
        for l in leads:
            writer.writerow(
                [
                    l.first_name,
                    l.last_name,
                    l.role,
                    l.company,
                    l.industry,
                    l.stage,
                    l.email,
                ]
            )
