# Capital Scout AI Outreach Agent

## Overview
This project builds a demo-friendly outreach automation pipeline that:
- Reads leads from CSV
- Generates personalized outreach copy (A/B + 2 follow-ups)
- Produces Instantly and Airtable import CSVs
- Writes a campaign plan and logs

## What You Need (Prereqs)
- Windows 10/11 (recommended) or macOS/Linux
- Python 3.11 installed and on PATH
- (Optional) OpenAI API key in `.env` or `OPENAI_API_KEY`
- Internet access only if you want real OpenAI generation

## Install From Scratch
1. Download the repo
   - Option A: `git clone https://github.com/calloftheNIGHT2023/Capital-Scout-AI.git`
   - Option B: Download ZIP from GitHub and unzip
2. Open a terminal in the project folder
3. Create and activate a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```
4. Install dependencies
```bash
pip install -r requirements.txt
```
5. (Optional) Add OpenAI API key
   - Create `.env` in the project root:
```
OPENAI_API_KEY=your_key_here
```

## Run (Smoke Test / Demo)
```bash
python run_agent.py --input data/leads.csv --out outputs --campaign "week6-demo" --dry-run
```

## Run (Real OpenAI Generation)
```bash
python run_agent.py --input data/leads.csv --out outputs --campaign "week6-demo"
```

## Desktop App
```bash
python app_desktop.py
```

## Build Windows EXE
```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```
The output will be in `dist/CapitalScoutAI.exe`.

## Outputs
- `outputs/leads_clean.csv`
- `outputs/outreach_pack.json`
- `outputs/instantly_import.csv`
- `outputs/airtable_import.csv`
- `outputs/campaign_plan.md`
- `outputs/logs/run.log`

## How To Use The Outputs
- Instantly: import `outputs/instantly_import.csv` to create the campaign and split A/B variants
- Airtable: import `outputs/airtable_import.csv` into a base for tracking

## Screenshots (Placeholders)
### Apollo Export

### OpenAI Prompt + Output

### Instantly Campaign Screen

### Airtable Table
