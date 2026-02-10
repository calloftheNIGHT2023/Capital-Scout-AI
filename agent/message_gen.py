import json
import os
from typing import Dict
import requests
from .schemas import Lead, MessagePack
from .validators import validate_message_pack


def _demo_pack(lead: Lead) -> MessagePack:
    # Deterministic placeholder copy for demos and dry-run mode
    base = (
        f"[DEMO COPY] Hi {lead.first_name}, I track early teams in {lead.industry}. "
        f"Would you be open to a short intro chat next week?"
    )
    return MessagePack(
        subject_A=f"[DEMO COPY] Quick intro, {lead.first_name}",
        body_A=base,
        subject_B=f"[DEMO COPY] {lead.company} intro?",
        body_B=base,
        followup_1=f"[DEMO COPY] Following up, {lead.first_name}. Happy to share context if helpful.",
        followup_2=f"[DEMO COPY] Final check-in, {lead.first_name}. Open to a brief intro?",
    )


def _build_prompt(lead: Lead, buzzwords) -> str:
    # Prompt forces JSON-only output with strict constraints
    return (
        "You are an outreach assistant. Return ONLY valid JSON with keys: "
        "subject_A, body_A, subject_B, body_B, followup_1, followup_2. "
        "Constraints: body_A and body_B <= 120 words, no emojis, use only ASCII characters, "
        f"no buzzwords: {buzzwords}. Tone: warm, respectful, direct, non-salesy. "
        "Goal: invite a short intro conversation. No meta commentary. "
        f"Lead: first_name={lead.first_name}, last_name={lead.last_name}, role={lead.role}, "
        f"company={lead.company}, industry={lead.industry}, stage={lead.stage}."
    )


def _build_strict_prompt(lead: Lead, buzzwords) -> str:
    # Tighter instruction for retry attempts
    return (
        _build_prompt(lead, buzzwords)
        + " Return only JSON with double quotes and no trailing text. Any emoji or non-ASCII character makes the response invalid."
    )


def generate_message_pack(lead: Lead, settings: Dict, dry_run: bool = False) -> MessagePack:
    # DRY_RUN skips any external calls and always returns demo copy
    if dry_run:
        return _demo_pack(lead)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _demo_pack(lead)

    url = "https://api.openai.com/v1/chat/completions"
    model = settings.get("model", "gpt-4o-mini")
    temperature = settings.get("temperature", 0.4)
    max_tokens = settings.get("max_tokens", 450)
    buzzwords = settings.get("buzzwords", [])

    # Try up to 3 times: initial + 2 stricter retries
    for attempt in range(3):
        prompt = _build_prompt(lead, buzzwords) if attempt == 0 else _build_strict_prompt(lead, buzzwords)
        payload = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": "You write concise outreach messages."},
                {"role": "user", "content": prompt},
            ],
        }
        try:
            resp = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            data = json.loads(content)
            pack = MessagePack(**data)
            validate_message_pack(pack, settings)
            return pack
        except Exception:
            if attempt == 2:
                raise
            continue

    return _demo_pack(lead)
