# Author: Aditya Dogra
from __future__ import annotations

"""SMTP notification delivery.

Control flow:
1) Load SMTP config from environment with defaults.
2) Build text+HTML email payload.
3) Send with retry/backoff/jitter policy.
"""

from dataclasses import dataclass
import os
import random
import re
import smtplib
from email.message import EmailMessage
import time
from typing import Optional


@dataclass(frozen=True)
class SMTPConfig:
    host: str
    port: int
    username: Optional[str]
    password: Optional[str]
    from_email: str
    use_starttls: bool
    use_ssl: bool
    retries: int
    backoff_seconds: float
    jitter_seconds: float


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_smtp_config() -> SMTPConfig:
    # Section 1: Parse env vars into a validated SMTP configuration object.
    host = os.getenv("IETF_WG_SMTP_HOST", "localhost").strip() or "localhost"

    port_str = os.getenv("IETF_WG_SMTP_PORT", "25").strip()
    try:
        port = int(port_str)
    except ValueError as exc:
        raise ValueError("IETF_WG_SMTP_PORT must be an integer") from exc

    username = os.getenv("IETF_WG_SMTP_USERNAME")
    password = os.getenv("IETF_WG_SMTP_PASSWORD")
    from_email = os.getenv("IETF_WG_FROM_EMAIL", "").strip()
    if not from_email:
        from_email = username.strip() if username else "ietf-wg-agent@localhost"

    use_ssl = _env_bool("IETF_WG_SMTP_SSL", default=False)
    use_starttls = _env_bool("IETF_WG_SMTP_STARTTLS", default=False)
    retries_str = os.getenv("IETF_WG_SMTP_RETRIES", "3").strip()
    backoff_str = os.getenv("IETF_WG_SMTP_BACKOFF_SECONDS", "1.5").strip()
    jitter_str = os.getenv("IETF_WG_SMTP_JITTER_SECONDS", "0.5").strip()
    try:
        retries = int(retries_str)
    except ValueError as exc:
        raise ValueError("IETF_WG_SMTP_RETRIES must be an integer") from exc
    try:
        backoff_seconds = float(backoff_str)
    except ValueError as exc:
        raise ValueError("IETF_WG_SMTP_BACKOFF_SECONDS must be a number") from exc
    try:
        jitter_seconds = float(jitter_str)
    except ValueError as exc:
        raise ValueError("IETF_WG_SMTP_JITTER_SECONDS must be a number") from exc

    return SMTPConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        from_email=from_email,
        use_starttls=use_starttls,
        use_ssl=use_ssl,
        retries=max(retries, 1),
        backoff_seconds=max(backoff_seconds, 0.0),
        jitter_seconds=max(jitter_seconds, 0.0),
    )


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _render_html_from_text(text: str) -> str:
    # Section 2: Convert plain text report to compact HTML sections.
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "<html><body><p>No content</p></body></html>"

    title = _escape_html(lines[0])
    recipient = ""
    sections: list[tuple[str, list[str]]] = []
    current_title = ""
    current_items: list[str] = []

    for line in lines[1:]:
        if line.lower().startswith("recipient:"):
            recipient = _escape_html(line.split(":", 1)[1].strip())
            continue
        if line.startswith("WG:"):
            if current_title:
                sections.append((current_title, current_items))
            current_title = _escape_html(line[3:].strip())
            current_items = []
            continue
        if line.startswith("WG charter summary:"):
            continue
        if line.startswith("- "):
            current_items.append(_escape_html(line[2:].strip()))
        else:
            current_items.append(_escape_html(line))

    if current_title:
        sections.append((current_title, current_items))

    section_html = []
    for sec_title, items in sections:
        acronym = re.sub(r"[^A-Za-z0-9-]", "", sec_title).lower()
        wg_link = (
            f"https://datatracker.ietf.org/wg/{acronym}/about/" if acronym else ""
        )
        bullets = "".join(f"<li>{item}</li>" for item in items)
        link_html = (
            f'<a href="{wg_link}" style="font-size:12px; color:#1d4ed8; text-decoration:none;">WG page</a>'
            if wg_link
            else ""
        )
        section_html.append(
            f"""
            <section style="margin:0 0 14px 0; padding:10px 12px; border:1px solid #d7dde5; border-radius:8px;">
              <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; margin:0 0 8px 0;">
                <h3 style="margin:0; font-size:14px;">{sec_title}</h3>
                {link_html}
              </div>
              <ul style="margin:0; padding-left:18px;">{bullets}</ul>
            </section>
            """
        )

    recipient_html = (
        f'<p style="margin:0 0 10px 0; color:#4b5563;">Recipient: {recipient}</p>'
        if recipient
        else ""
    )
    return f"""\
<html>
  <body style="font-family:Arial,sans-serif; line-height:1.5; color:#1a1a1a; background:#f7f9fc; margin:0; padding:16px;">
    <div style="max-width:760px; margin:0 auto; background:#ffffff; border:1px solid #e5e7eb; border-radius:10px; padding:14px 16px;">
      <h2 style="margin:0 0 8px 0;">{title}</h2>
      {recipient_html}
      {''.join(section_html)}
    </div>
  </body>
</html>
"""


def send_email(to_email: str, subject: str, body: str, config: SMTPConfig) -> None:
    # Section 3: Attempt SMTP send with exponential-backoff retry.
    msg = EmailMessage()
    msg["From"] = config.from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    msg.add_alternative(_render_html_from_text(body), subtype="html")

    smtp_cls = smtplib.SMTP_SSL if config.use_ssl else smtplib.SMTP
    last_exc: Optional[Exception] = None
    for attempt in range(1, config.retries + 1):
        try:
            with smtp_cls(config.host, config.port, timeout=30) as server:
                if config.use_starttls and not config.use_ssl:
                    server.starttls()
                if config.username and config.password:
                    server.login(config.username, config.password)
                server.send_message(msg)
            return
        except Exception as exc:
            last_exc = exc
            if attempt == config.retries:
                break
            base_sleep = config.backoff_seconds * (2 ** (attempt - 1))
            jitter = random.uniform(0.0, config.jitter_seconds)
            sleep_seconds = base_sleep + jitter
            time.sleep(sleep_seconds)

    if last_exc:
        raise last_exc
