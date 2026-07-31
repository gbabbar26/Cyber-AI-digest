# 📰 Cyber + AI Daily Digest

A free, self-hosted daily email digest of cybersecurity and AI news built with
Claude (web search) + live Reddit discussions. Runs automatically on GitHub Actions
at zero infrastructure cost. Fully customizable to any topic, not just cyber/AI.

Built because generic news apps don't let you filter tightly enough for a specific
field this gives you a focused, skimmable digest every morning in your inbox.

## What you get each morning

- Top cybersecurity stories (breaches, CVEs, patches) with why-it-matters context
- Top AI stories (new models, safety research, company news)
- What practitioners are actually discussing on Reddit right now
- One concept/tool explained in beginner-friendly terms, so it doubles as a learning tool

## Quick start (10 minutes, no server needed)

1. **Fork this repo** (button top-right)
2. Get a free-tier [Anthropic API key](https://console.anthropic.com) cost is roughly $0.02–$0.10 per run
3. Create a [Gmail App Password](https://myaccount.google.com/apppasswords) (requires 2-Step Verification on your Google account)
4. In your fork: **Settings → Secrets and variables → Actions**, add:

   | Secret | Value |
   |---|---|
   | `ANTHROPIC_API_KEY` | your Anthropic key |
   | `EMAIL_FROM` | Gmail address sending the digest |
   | `EMAIL_TO` | address you want it delivered to |
   | `EMAIL_APP_PASSWORD` | the 16-character app password |

5. Edit `config.yaml` to set your topics, subreddits, and title (see below)
6. Edit the `cron` line in `.github/workflows/daily-digest.yml` for your preferred time (GitHub Actions uses UTC [crontab.guru](https://crontab.guru) helps)
7. Go to the **Actions** tab → "Daily Cyber + AI Digest" → **Run workflow** to test it manually
8. Once it works, it runs automatically every day — no server, no computer needed

## Customizing for any topic

This isn't locked to cyber/AI edit `config.yaml`:

```yaml
digest_title: "Climate Tech Weekly"
topics: "climate technology, renewable energy, and carbon capture startups"
subreddits:
  - ClimateTech
  - energy
reddit_posts_per_sub: 5
model: "claude-sonnet-4-6"
```

No code changes needed the script reads everything from this file.

## Local testing

```bash
git clone <your-fork-url>
cd cyber-ai-digest
pip install -r requirements.txt
cp .env.example .env   # fill in your real values
export $(cat .env | xargs)  # or use a tool like python-dotenv
python digest.py
```

## Cost

Roughly $0.60–$3/month running daily, depending on how much web search Claude does
per run. GitHub Actions itself is free for public repos and has a generous free
tier for private ones too.

## How it works

1. `digest.py` pulls hot threads from your configured subreddits via Reddit's public
   JSON endpoints (no Reddit API key required)
2. Sends that context + a research prompt to Claude, which uses web search to find
   current news and synthesizes everything into a structured Markdown digest
3. Emails the result via Gmail SMTP
4. A GitHub Actions cron job triggers this automatically every day

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs and topic-config examples welcome.
