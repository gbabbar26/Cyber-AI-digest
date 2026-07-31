"""
Cyber + AI Daily News Digest
Pulls hot Reddit threads (cybersecurity/AI subs) + uses Claude with web search
to build a synthesized digest, then emails it to you.
"""

import os
import smtplib
import urllib.request
import json
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

import anthropic

# ---------- Config ----------
# Topic/subreddit/schedule settings live in config.yaml so users can customize
# without touching code. Secrets (API keys, email creds) stay in environment
# variables / GitHub Secrets — never put those in config.yaml.
CONFIG_PATH = os.environ.get("DIGEST_CONFIG", "config.yaml")

with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

SUBREDDITS = CONFIG.get("subreddits", ["cybersecurity", "netsec", "artificial"])
REDDIT_POSTS_PER_SUB = CONFIG.get("reddit_posts_per_sub", 5)
TOPICS = CONFIG.get("topics", "cybersecurity and AI")
MODEL = CONFIG.get("model", "claude-sonnet-4-6")
DIGEST_TITLE = CONFIG.get("digest_title", "Cyber + AI Daily Digest")

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]  # Gmail App Password, not your real password


# ---------- Step 1: Pull Reddit hot threads (no API key needed, public JSON) ----------
def fetch_reddit_highlights():
    highlights = []
    headers = {"User-Agent": "cyber-ai-digest-bot/1.0"}
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit={REDDIT_POSTS_PER_SUB}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            for post in data["data"]["children"]:
                p = post["data"]
                if p.get("stickied"):
                    continue
                highlights.append({
                    "subreddit": sub,
                    "title": p.get("title"),
                    "score": p.get("score"),
                    "comments": p.get("num_comments"),
                    "url": f"https://reddit.com{p.get('permalink')}",
                })
        except Exception as e:
            print(f"Warning: could not fetch r/{sub}: {e}")
    return highlights


# ---------- Step 2: Ask Claude to research + synthesize a digest ----------
def build_digest(reddit_highlights):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    reddit_text = "\n".join(
        f"- [r/{h['subreddit']}] {h['title']} ({h['score']} upvotes, {h['comments']} comments) {h['url']}"
        for h in reddit_highlights
    )

    prompt = f"""You are building a daily news digest EXCLUSIVELY about {TOPICS}.
Today's date: {date.today().isoformat()}.

Use web search to find the most important news on these topics from the last 24-48 hours:
- New vulnerabilities / CVEs, breaches, exploits, patches
- AI security research (jailbreaks, model safety, adversarial ML)
- Major AI company announcements (new models, tools, policy changes)
- Major cybersecurity company/vendor news
- Notable regulatory or policy developments in AI or cyber

Here are hot Reddit discussions happening right now in relevant subreddits, use these as
signal for what practitioners are currently talking about, and weave in any that are genuinely
newsworthy (ignore low-value/meme posts):

{reddit_text}

Produce a clean digest in Markdown with this structure:
# {DIGEST_TITLE} — {date.today().strftime('%B %d, %Y')}

## 🔐 Top Cybersecurity Stories
(3-5 items, each: **Headline** — 1-2 sentence summary — why it matters for someone job-hunting in security)

## 🤖 Top AI Stories
(3-5 items, same format)

## 💬 What Practitioners Are Discussing (Reddit)
(2-4 genuinely interesting threads, with a one-line takeaway each)

## 📌 One Thing To Learn About Today
(pick ONE concept/tool/CVE from the above and explain it in 3-4 sentences, beginner-friendly,
since this digest is for someone learning cybersecurity)

Keep it concise and skimmable. No fluff, no generic intros."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    text_parts = [block.text for block in response.content if block.type == "text"]
    return "\n\n".join(text_parts)


# ---------- Step 3: Email it ----------
def send_email(markdown_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{DIGEST_TITLE} — {date.today().strftime('%b %d, %Y')}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    msg.attach(MIMEText(markdown_body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

    print("Email sent successfully.")


if __name__ == "__main__":
    print("Fetching Reddit highlights...")
    reddit_data = fetch_reddit_highlights()
    print(f"Got {len(reddit_data)} Reddit posts.")

    print("Building digest with Claude...")
    digest = build_digest(reddit_data)

    print("Sending email...")
    send_email(digest)

    print("Done.")
