import csv
import json
import os
from typing import List, Dict
from .schemas import Lead, MessagePack


def write_outreach_pack(path: str, leads: List[Lead], packs: Dict[str, MessagePack]) -> None:
    items = []
    for lead in leads:
        items.append(
            {
                "lead": lead.model_dump(),
                "messages": packs[lead.email].model_dump(),
            }
        )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def write_instantly_csv(path: str, leads: List[Lead], packs: Dict[str, MessagePack]) -> None:
    headers = [
        "email",
        "first_name",
        "last_name",
        "company",
        "role",
        "industry",
        "stage",
        "subject",
        "body",
        "followup_1",
        "followup_2",
        "variant",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for lead in leads:
            pack = packs[lead.email]
            # Two rows per lead for A/B testing
            writer.writerow(
                [
                    lead.email,
                    lead.first_name,
                    lead.last_name,
                    lead.company,
                    lead.role,
                    lead.industry,
                    lead.stage,
                    pack.subject_A,
                    pack.body_A,
                    pack.followup_1,
                    pack.followup_2,
                    "A",
                ]
            )
            writer.writerow(
                [
                    lead.email,
                    lead.first_name,
                    lead.last_name,
                    lead.company,
                    lead.role,
                    lead.industry,
                    lead.stage,
                    pack.subject_B,
                    pack.body_B,
                    pack.followup_1,
                    pack.followup_2,
                    "B",
                ]
            )


def write_airtable_csv(path: str, leads: List[Lead], packs: Dict[str, MessagePack]) -> None:
    headers = [
        "Name",
        "Role",
        "Company",
        "Industry",
        "Stage",
        "Email",
        "Source",
        "Email Version",
        "Opened",
        "Replied",
        "Interested",
        "Notes",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for lead in leads:
            for variant in ["A", "B"]:
                writer.writerow(
                    [
                        f"{lead.first_name} {lead.last_name}",
                        lead.role,
                        lead.company,
                        lead.industry,
                        lead.stage,
                        lead.email,
                        lead.source,
                        variant,
                        "",
                        "",
                        "",
                        "",
                    ]
                )


def write_campaign_plan(path: str, campaign: str) -> None:
    content = f"""# Campaign Plan: {campaign}

## Sequence Timing
- Day 1: Initial outreach (Variant A/B split)
- Day 4: Follow-up 1
- Day 8: Follow-up 2

## A/B Logic
- Each lead is exported twice: Variant A and Variant B
- Instantly can split the list to test subject/body performance

## Demo Screenshots
- Apollo export CSV
- OpenAI prompt + JSON output
- Instantly campaign screen (sequence + A/B settings)
- Airtable table import

## Privacy Note
- All data is anonymized and intended for demo use only
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def ensure_dirs(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "logs"), exist_ok=True)
