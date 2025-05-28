# DiscordSummarizer Project

## Overview

`DiscordSummarizer.py` is a simple Discord bot that:

1. Tracks a per-channel "last-read" timestamp
2. Fetches all new messages since that timestamp
3. Uses the OpenAI API to generate an adaptive-length summary of each channel's unread messages
4. DMs the summary to the user who invoked the `!summarize` command
5. Supports `!markread` to advance the "last-read" timestamp without summarizing

This repository only includes `DiscordSummarizer.py` and a `.env` template; all other files (e.g., `last_read.json`, virtual environments, logs) should be listed in `.gitignore`.

## Requirements

* Python 3.9 or higher
* An active OpenAI API key
* A Discord Bot with the following Gateway Intent enabled:
  • Message Content Intent

## Dependencies

Install via pip:

```
pip install discord.py openai python-dotenv
```

## .env File Template

Create a file named `.env` in the same directory as `DiscordSummarizer.py`, then fill in your credentials:

```
# Discord bot token (from Discord Developer Portal)
DISCORD_BOT_TOKEN=your_bot_token_here

# Comma-separated list of source channel IDs (text channels to summarize)
DISCORD_SOURCE_CHANNEL_IDS=123456789012345678,234567890123456789

# (Optional) Where to store last-read timestamps (defaults to last_read.json)
LAST_READ_FILE=last_read.json

# OpenAI API key (from platform.openai.com/account/api-keys)
OPENAI_API_KEY=sk-...

# (Optional) Model to use for summarization (defaults to gpt-3.5-turbo)
OPENAI_MODEL=gpt-3.5-turbo
```

## Usage

1. Start the bot:

   ```
   python DiscordSummarizer.py
   ```

2. In Discord (in any channel the bot can see or in a DM with it), run:

   ```
   !summarize
   ```

   The bot will DM you a consolidated summary of all new messages since your last run.

3. To reset the "last-read" markers without generating a summary, run:

   ```
   !markread
   ```

## Notes

* Make sure your bot has the following permissions in each source channel:
  • View Channels
  • Read Message History
  • Send Messages (for replying in DMs)

* On first run, if `last_read.json` does not exist, the bot will default to 24 hours ago.

* To include full history on initial run, delete or rename `last_read.json` before starting.

## License & Acknowledgments

This project uses the `discord.py` library and the OpenAI API. Ensure you comply with their respective licenses and Terms of Service.
