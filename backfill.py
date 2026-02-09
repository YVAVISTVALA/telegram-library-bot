import asyncio
import csv
import os
import re
from telethon import TelegramClient

API_ID = int(os.getenv("TG_API_ID", "0"))
API_HASH = os.getenv("TG_API_HASH")
CHANNEL = os.getenv("TG_CHANNEL")  # e.g. -1001234567890, @channelusername, or t.me/c/... link
OUTPUT = os.getenv("OUT_CSV", "books.csv")

if not API_ID or not API_HASH or not CHANNEL:
    raise SystemExit("Set TG_API_ID, TG_API_HASH, TG_CHANNEL env vars")

TAG_RE = re.compile(r"#([\w-]+)")


def extract_title(message):
    if message.message and message.message.strip():
        line = message.message.splitlines()[0].strip()
        if line:
            return line
    if message.file and message.file.name:
        return message.file.name.rsplit(".", 1)[0]
    return "Untitled"


def extract_topic(message):
    if message.message:
        match = TAG_RE.search(message.message)
        if match:
            return match.group(1).replace("_", " ")
    if getattr(message, "reply_to", None) and getattr(message.reply_to, "reply_to_top_id", None):
        return f"topic-{message.reply_to.reply_to_top_id}"
    return ""


def _normalize_channel(value: str):
    if not value:
        return value
    v = value.strip()
    if v.startswith("https://t.me/c/"):
        # https://t.me/c/<id>/<msg>
        parts = v.split("/c/")[-1].split("/")
        if parts and parts[0].isdigit():
            return int("-100" + parts[0])
    if v.startswith("https://web.telegram.org/") and "#-" in v:
        try:
            return int(v.rsplit("#", 1)[-1])
        except ValueError:
            return v
    if v.lstrip("-").isdigit():
        return int(v)
    return v


async def main():
    client = TelegramClient("backfill", API_ID, API_HASH)
    await client.start()

    channel = _normalize_channel(CHANNEL)
    try:
        entity = await client.get_entity(channel)
    except Exception as exc:
        raise SystemExit(
            "Cannot find channel. Ensure your personal account is a member of the channel "
            "and TG_CHANNEL is correct (e.g. -100..., @username, or https://t.me/c/... link)."
        ) from exc

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "topic", "message_id"])

        async for msg in client.iter_messages(entity):
            if not msg.file:
                continue
            name = (msg.file.name or "").lower()
            if not (name.endswith(".pdf") or name.endswith(".epub")):
                continue
            title = extract_title(msg)
            topic = extract_topic(msg)
            writer.writerow([title, topic, msg.id])

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
