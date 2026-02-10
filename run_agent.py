import argparse
import os
import sys
import yaml
from dotenv import load_dotenv
from rich.console import Console

from agent.lead_source import read_leads_csv, write_clean_csv
from agent.message_gen import generate_message_pack
from agent.artifacts import (
    ensure_dirs,
    write_outreach_pack,
    write_instantly_csv,
    write_airtable_csv,
    write_campaign_plan,
)
from agent.logger import setup_logger


def load_settings(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description="Capital Scout AI outreach agent")
    parser.add_argument("--input", required=True, help="Path to leads CSV")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--campaign", required=True, help="Campaign name")
    parser.add_argument("--dry-run", action="store_true", help="Generate files only")
    parser.add_argument("--config", default="config.yaml", help="Config YAML path")
    args = parser.parse_args()

    load_dotenv()
    settings = load_settings(args.config)

    ensure_dirs(args.out)
    log_path = os.path.join(args.out, "logs", "run.log")
    logger = setup_logger(log_path)

    console = Console()
    console.print("[bold]Capital Scout AI[/bold]")

    logger.info("Loading leads from %s", args.input)
    leads = read_leads_csv(args.input)
    logger.info("Loaded %d leads", len(leads))

    clean_path = os.path.join(args.out, "leads_clean.csv")
    write_clean_csv(clean_path, leads)
    logger.info("Wrote cleaned leads: %s", clean_path)

    packs = {}
    for lead in leads:
        logger.info("Generating messages for %s", lead.email)
        try:
            pack = generate_message_pack(lead, settings, dry_run=args.dry_run)
            packs[lead.email] = pack
        except Exception as exc:
            logger.error("Generation failed for %s: %s", lead.email, exc)
            return 1

    outreach_path = os.path.join(args.out, "outreach_pack.json")
    instantly_path = os.path.join(args.out, "instantly_import.csv")
    airtable_path = os.path.join(args.out, "airtable_import.csv")
    plan_path = os.path.join(args.out, "campaign_plan.md")

    write_outreach_pack(outreach_path, leads, packs)
    write_instantly_csv(instantly_path, leads, packs)
    write_airtable_csv(airtable_path, leads, packs)
    write_campaign_plan(plan_path, args.campaign)

    logger.info("Wrote outreach_pack.json")
    logger.info("Wrote Instantly import CSV")
    logger.info("Wrote Airtable import CSV")
    logger.info("Wrote campaign plan")

    if args.dry_run:
        logger.info("Dry run mode enabled. No external sends performed.")

    console.print("[green]Done[/green]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
