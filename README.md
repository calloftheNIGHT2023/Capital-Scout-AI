# Capital Scout AI Outreach Agent

## Overview
This project builds a demo-friendly outreach automation pipeline that:
- Reads leads from CSV
- Generates personalized outreach copy (A/B + 2 follow-ups)
- Produces Instantly and Airtable import CSVs
- Writes a campaign plan and logs

## Requirements
- Python 3.11
- An OpenAI API key in `.env` or `OPENAI_API_KEY` (optional; demo copy is generated if missing)

## Install
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run (Smoke Test)
```bash
python run_agent.py --input data/leads.csv --out outputs --campaign "week6-demo" --dry-run
```

## Outputs
- `outputs/leads_clean.csv`
- `outputs/outreach_pack.json`
- `outputs/instantly_import.csv`
- `outputs/airtable_import.csv`
- `outputs/campaign_plan.md`
- `outputs/logs/run.log`

## Screenshots (Placeholders)
### Apollo Export

### OpenAI Prompt + Output

### Instantly Campaign Screen

### Airtable Table
