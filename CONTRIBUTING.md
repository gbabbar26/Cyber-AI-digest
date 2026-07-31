# Contributing

Contributions are welcome! Ways to help:

- **New digest topics/templates** - share your `config.yaml` variants (e.g. cloud security, AI safety research) as examples in `examples/`
- **Additional delivery methods** - Slack/Discord webhook support, RSS feed output, etc.
- **Bug fixes / reliability** - e.g. better error handling if Reddit or the API is briefly down

## How to contribute

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-idea`
3. Make your change, test it locally (`python digest.py` with a `.env` file loaded)
4. Open a pull request describing what changed and why

## Reporting issues

Open a GitHub Issue with:
- What you expected to happen
- What actually happened (include the Actions log output if it's a workflow failure)
- Your `config.yaml` (with secrets removed, obviously)
